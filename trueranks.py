from sqlalchemy import or_, and_
import math
from collections import defaultdict

from tasbot.customlog import Log

from ranking import IRanking, RankingTable, calculateWinnerOrder
from db_entities import TrueskillRanks, Player
import trueskill

class TrueskillRankAlgo(IRanking):

	def Update(self,ladder_id,match,db):
		#print 'match id %d'%match.id
		scores, result_dict = calculateWinnerOrder(match,db)
		session = db.session()

		teams = defaultdict(tuple)
		player_id_map = defaultdict(list)
		def constant_factory(value):
			import itertools
			return itertools.repeat(value).next
		minteam_score = defaultdict(constant_factory(100000))
		for name,result in result_dict.iteritems():
			score = scores[name] * -1
			player_id = session.query( Player ).filter( Player.nick == name ).first().id
			rank = session.query( TrueskillRanks ).filter( TrueskillRanks.ladder_id == ladder_id ).filter( TrueskillRanks.player_id == player_id ).first()
			if not rank:
				rank = TrueskillRanks()
				rank.ladder_id = ladder_id
				rank.player_id = player_id
			session.add(rank)

			rank.rank = score
			l = list(teams[result.team])
			l.append(rank.rating)
			teams[result.team] = tuple(l)
			player_id_map[result.team].append(player_id)
			minteam_score[result.team] = min(minteam_score[result.team],score)
		session.commit()

		ordered_teams = []
		ordered_minteam_score = []
		team_ids = teams.keys()
		team_ids.sort()
		for i in range(len(teams)):
			ordered_teams.append(teams[team_ids[i]])
			ordered_minteam_score.append(minteam_score[team_ids[i]])
		i = 0
		if len(ordered_teams) < 2:
			Log.error('less than 2 teams, cannot update ranking')
			raise Exception('not enough teams')
		for team_ratings in trueskill.transform_ratings(ordered_teams,ordered_minteam_score):
			j = 0
			current_team = team_ids[i]
			q = session.query( TrueskillRanks ).filter( TrueskillRanks.ladder_id == ladder_id )
			for rating in team_ratings:
				pids = player_id_map[current_team]
				pid = pids[j]
				rank = q.filter( TrueskillRanks.player_id == pid ).one()
				rank.rating = rating
				session.add( rank )
				j += 1
			i += 1
		session.commit()
		session.close()

	@staticmethod
	def GetPrintableRepresentation(rank_list,db):
		ret = '#position playername\t\t(mu/sigma):\n'
		s = db.session()
		count = 0
		previousrating = -1
		same_rating_in_a_row = 0
		for rank in rank_list:
			s.add( rank )
			if rank.mu != previousrating: # give the same position to players with the same rank
				if same_rating_in_a_row == 0:
					count += 1
				else:
					count += same_rating_in_a_row +1
					same_rating_in_a_row = 0
			else:
				same_rating_in_a_row += 1
			ret += '#%d %s\t(%4.2f/%3.4f)\n'%(count,rank.player.nick,rank.mu, rank.sigma)
			previousrating = rank.mu
		s.close()
		return ret

	def GetCandidateOpponents(self,player_nick,ladder_id,db):
		player = db.GetPlayer( player_nick )
		player_id = player.id
		session = db.session()
		playerrank = session.query( TrueskillRanks ).filter( TrueskillRanks.player_id == player_id ).filter( TrueskillRanks.ladder_id == ladder_id ).first()
		if not playerrank: # use default rank, but don't add it to the db yet
			playerrank = TrueskillRanks()
		playerminvalue = playerrank.rating - playerrank.rd
		playermaxvalue = playerrank.rating + playerrank.rd
		opponent_q = session.query( TrueskillRanks ).filter( TrueskillRanks.player_id != player_id ) \
			.filter( TrueskillRanks.ladder_id == ladder_id )
		ops1 = opponent_q \
			.filter( and_ ( ( (TrueskillRanks.rating + TrueskillRanks.rd) >= playerminvalue ), \
								 ( ( TrueskillRanks.rating + TrueskillRanks.rd ) <= playermaxvalue ) ) )
		ops2 = opponent_q \
			.filter( and_( ( playermaxvalue >=  ( TrueskillRanks.rating - TrueskillRanks.rd ) ), \
								( playermaxvalue <= (TrueskillRanks.rating + TrueskillRanks.rd) ) )  ) \
			#.order_by( math.fabs(TrueskillRanks.rating - playerrank.rating ) )
		opponents = []
		opponents_ranks = dict()
		ops = ops1.all() + ops2.all()
		ops.sort( lambda x,y : cmp( math.fabs( x.rating - playerrank.rating ), math.fabs( y.rating - playerrank.rating ) ) )
		for op in ops:
			opponents.append(op.player.nick)
			opponents_ranks[op.player.nick] = '#%d %s\t(%4.2f/%3.0f)\n'%(db.GetPlayerPosition(ladder_id, op.player.id),op.player.nick,op.rating, op.rd)
		session.close()
		return opponents, opponents_ranks

	def GetWebRepresentation(self,rank_list,db):
		ret = RankingTable()
		ret.header = ['nick','mu','sigma']
		ret.rows = []
		s = db.session()
		for rank in rank_list:
			s.add( rank )
			ret.rows.append( [rank.player.nick , round(rank.mu,2), round(rank.sigma,4) ] )
		s.close()
		return ret

	def GetDbEntityType(self):
		return TrueskillRanks

	def OrderByKey(self):
		return TrueskillRanks.mu.desc()
