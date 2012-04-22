from bottle import route,request, response
import PyRSS2Gen
import datetime
import cStringIO
import urllib

from fieldsets import getSingleField, MatchInfoToTableAdapter
from ladderdb import ElementNotFoundException
from ranking import EmptyRankingListException
from db_entities import Ladder, Match, Result
from globe import db,env,cache,config

def get_items(query):
	items = []
	base_url = config.get('ladder', 'base_url')
	for match in query:	
		url = '%s/%s' % (base_url, urllib.quote('match?id=%s'%(match.id)))
		#$postdate = date("Y-m-d H:i", $row['topic_time']);
		title = '%s'%(match.mapname)
		template = env.get_template('rss_match.html')
		desc = template.render(ladder=match.ladder, matchinfo=MatchInfoToTableAdapter(match),base_url=base_url )
		items.append( PyRSS2Gen.RSSItem( title = title, link=url, guid = PyRSS2Gen.Guid( url ), pubDate=match.date, description = desc ) )
	return items

@route('/feeds/matches/:ladder_id')
def matches_rss(ladder_id):
	@cache.cache('get_rss_out_matches_single_ladder', expire=300)
	def get_rss_out(l_id):
		try:
			base_url = config.get('ladder', 'base_url')
			s = db.sessionmaker()
			limit = 10
			matches = s.query( Match ).filter( Match.ladder_id == l_id )
			ladder_name = s.query( Ladder.name ).filter( Ladder.id == l_id ).one()
			items = get_items( matches )
			if len(items) == 0:
				return ""
			rss = PyRSS2Gen.RSS2(
				title = "%s -- Latest matches"%ladder_name,
				link = "%sfeeds/matches/%s"%(base_url,l_id),
				description = "Latest 10 matches played on a single given ladder",
				lastBuildDate = datetime.datetime.now(),
				items = items )
			output = cStringIO.StringIO()
			rss.write_xml(output)
			response.headers['Content-Type'] = 'text/xml'
			return output.getvalue()
		
		except Exception, m:
			if 's' in locals() and s:
				s.close()
			return str(m)
			
	response.headers['Content-Type'] = 'text/xml'
	return get_rss_out(ladder_id)
	
@route('/feeds/matches')
def all_matches_rss():
	@cache.cache('all_get_rss_out_matches_all', expire=300)
	def all_get_rss_out():
		try:
			base_url = config.get('ladder', 'base_url')
			s = db.sessionmaker()
			limit = 10
			matches = s.query( Match )
			items = get_items( matches )
			if len(items) == 0:
				return ""
			rss = PyRSS2Gen.RSS2(
				title = "SpringLadder -- Latest matches",
				link = "%s/feeds/matches"%(base_url),
				description = "Latest 10 matches played on any ladder",
				lastBuildDate = datetime.datetime.now(),
				items = items )
			output = cStringIO.StringIO()
			rss.write_xml(output)
			return output.getvalue()
		
		except Exception, m:
			if 's' in locals() and s:
				s.close()
			return str(m)
			
	response.headers['Content-Type'] = 'text/xml'
	return all_get_rss_out()	

from ranking import GlobalRankingAlgoSelector

@route('/feeds/scores/:ladder_id')
def scores_rss(ladder_id):
	@cache.cache('get_rss_out_scores_single_ladder', expire=300)
	def get_rss_out(l_id):
		s = None
		try:
			base_url = config.get('ladder','base_url')
			s = db.sessionmaker()			
			lad = db.GetLadder( ladder_id )
			rank_table = GlobalRankingAlgoSelector.GetWebRepresentation( db.GetRanks( ladder_id ), db )
			#template = env.get_template('scoreboard.html')
			template = env.get_template('rss_scoreboard.html')
			desc = template.render( rank_table=rank_table, ladder=lad )
			url = '%sscoreboard?id=%s'%(base_url,ladder_id)
			#$postdate = date("Y-m-d H:i", $row['topic_time']);
			title = "%s -- updated scoreboard"%lad.name
			
			item = PyRSS2Gen.RSSItem( title = title, link=url, guid = PyRSS2Gen.Guid( url ), pubDate=datetime.datetime.now(), description = desc )
			rss = PyRSS2Gen.RSS2(
				title = "%s -- Scoreboard"%lad.name,
				link = "%sfeeds/scores/%s"%(base_url,l_id),
				description = "DESCRIPTION",
				lastBuildDate = datetime.datetime.now(),
				items = [item] )
			output = cStringIO.StringIO()
			rss.write_xml(output)
			return output.getvalue()
		
		except Exception, m:
			if 's' in locals() and s:
				s.close()
			return str(m)
			
	response.headers['Content-Type'] = 'text/xml'
	return get_rss_out(ladder_id)
