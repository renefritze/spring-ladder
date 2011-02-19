# -*- coding: utf-8 -*-
from ranking import IRanking,RankingTable,calculateWinnerOrder
from db_entities import TrueskillRanks,Player,Match,Result
from sqlalchemy import or_, and_
import math,time,datetime
from trueskill import trueskill

class TrueskillRankAlgo(IRanking):

	def Update(self,ladder_id,match,db):
		scores, result_dict = calculateWinnerOrder(match,db)
		session = db.sessionmaker()
		ranks = []
		
		for name,result in result_dict.iteritems():
			
			player_id = session.query( Player ).filter( Player.nick == name ).first().id
			rank = session.query( TrueskillRanks ).filter( TrueskillRanks.ladder_id == ladder_id ).filter( TrueskillRanks.player_id == player_id ).first()
			if not rank:
				rank = TrueskillRanks()
				rank.ladder_id = ladder_id
				rank.player_id = player_id
			session.add(rank)
			#our trueskill lib assumes lowest score <--> winner
			rank.rank = scores[name] * -1 
			#must i commit everytime?
			session.commit()
			ranks.append( rank )

		trueskill.AdjustPlayers(ranks)
		for rank in ranks:
			session.add ( rank )
		session.commit()

		session.close()

	@staticmethod
	def GetPrintableRepresentation(rank_list,db):
		ret = '#position playername\t\t(mu/sigma):\n'
		s = db.sessionmaker()
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
			ret += '#%d %s\t(%4.2f/%3.0f)\n'%(count,rank.player.nick,rank.mu, rank.sigma)
			previousrating = rank.mu
		s.close()
		return ret

	def GetCandidateOpponents(self,player_nick,ladder_id,db):
		player = db.GetPlayer( player_nick )
		player_id = player.id
		session = db.sessionmaker()
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
		ret.header = ['nick','rating','RD']
		ret.rows = []
		s = db.sessionmaker()
		for rank in rank_list:
			s.add( rank )
			ret.rows.append( [rank.player.nick , round(rank.mu,2), round(rank.sigma,4) ] )
		s.close()
		return ret

	def GetDbEntityType(self):
		return TrueskillRanks

	def OrderByKey(self):
		return TrueskillRanks.mu.desc()
