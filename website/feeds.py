#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fieldsets import getSingleField
from ladderdb import ElementNotFoundException, EmptyRankingListException
from db_entities import Ladder, Match, Result
from bottle import route,request
from globe import db,env,cache,config
import PyRSS2Gen, datetime, cStringIO

@route('/feeds/matches/:ladder_id')
def matches_rss(ladder_id):
	#@cache.cache('fame_output', expire=60)
	def get_rss_out(l_id):
		print 'not cached: get_rss_out(%s)'%str(l_id)
		try:
			base_url = config['base_url']
			s = db.sessionmaker()
			limit = 10
			matches = s.query( Match ).filter( Match.ladder_id == l_id )
			items = []
			for match in matches:
				
				url = '%smatch?id=%s'%(base_url,match.id)
				#$postdate = date("Y-m-d H:i", $row['topic_time']);
				title = '%s'%(match.mapname)
				items.append( PyRSS2Gen.RSSItem( title = title, link=url, guid = PyRSS2Gen.Guid( url ), pubDate=match.date ) )
			rss = PyRSS2Gen.RSS2(
				title = "%s -- Latest matches"%match.ladder.name,
				link = "%sfeeds/matches/%s"%(base_url,l_id),
				description = "DESCRIPTION",
				lastBuildDate = datetime.datetime.now(),
				items = items )
			output = cStringIO.StringIO()
			rss.write_xml(output)
			return output.getvalue()
		
		except Exception, m:
			if s:
				s.close()
			return str(m)
			
	return get_rss_out(ladder_id)