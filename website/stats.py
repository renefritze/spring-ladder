#!/usr/bin/python
# -*- coding: utf-8 -*-
from formalchemy import Field, types
from sqlalchemy import func
from ladderdb import *
from fieldsets import getSingleField, MatchInfoToTableAdapter
from bottle import route,request
import datetime
from globe import db,env,config,disqus
from ranking import EmptyRankingListException

@route('/stats')
def output( ):
	try:
		s = db.session()
		stats = dict()
		stats['playercount'] = s.query(Player.id).count()
		matches = s.query(Match)
		stats['matchcount'] = matches.count()
		#stats['totalduration'] = s.query(func.sum(Match.duration).label('sum'))['sum']
		#kk = s.query(Match.duration).all()
		#print kk
		stats['totalduration'] = sum([f[0] for f in s.query(Match.duration).all()], datetime.timedelta())
		stats['avgduration'] = str(datetime.timedelta(seconds=stats['totalduration'].total_seconds() / float(stats['matchcount'])))
		stats['totalduration'] = str(stats['totalduration'] )
		stats['mostplayedmap'] = s.query(Match.mapname,func.count(Match.mapname).label('count')).group_by(Match.mapname).order_by('count DESC').first()
		stats['mostplayedgame'] = s.query(Match.modname,func.count(Match.modname).label('count')).group_by(Match.modname).order_by('count DESC').first()
		#stats['avgplayercount'] = func.avg(Match.
		print stats

		s.close()
		template = env.get_template('stats.html')
		return template.render(stats=stats)
		
	except ElementNotFoundException, e:
		err_msg="ladder with id %s not found"%(str(id))
	except EmptyRankingListException, m:
		err_msg=(str(m))
	except Exception, c:
		err_msg=(str(c))

	if s:
		s.close()
	template = env.get_template('error.html')
	return template.render( err_msg=err_msg )
