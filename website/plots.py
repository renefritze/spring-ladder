#!/usr/bin/env python
# -*- coding: utf-8 -*-
from globe import config, cache,db
from datetime import timedelta,datetime,date,time
import matplotlib 
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from db_entities import Match,Player,Result

from threading import Lock
mutex = Lock()

fail_offset = timedelta(days=363)

@cache.cache('matches_per_ladder',expire=3600)
def matches_per_ladder( ladderid ):
	print 'not cached: matches_per_ladder( %s )'% ladderid
	s = db.sessionmaker()
	inc = timedelta(days=1)
	today = datetime.combine(date.today(), time.min ) #datetime( now.year, now.month, now.day )
	since = today - timedelta(days=7) - fail_offset
	now = since
	data = []
	i = 1
	while now < datetime.now() - fail_offset:
		data.append( s.query( Match.id ).filter( Match.ladder_id == ladderid).filter( Match.date < now + inc ).filter( Match.date >= now ).count() )
		i += 1
		now += inc
	fn = 'images/plots/ladder_matches_%i.png'%int(ladderid)
	with mutex:
		f = plt.figure(1)
		plt.plot(range(len(data)),data)
		plt.ylabel('matches per day')
		plt.xlabel('days past')
		plt.savefig(config['base_dir']+fn,transparent=True)
		plt.close(1)
	s.close()
	return config['base_url'] + fn
	
@cache.cache('matches_per_player',expire=3600)
def matches_per_player( playerid ):
	print 'not cached: matches_per_player( %s )'% playerid
	s = db.sessionmaker()
	inc = timedelta(days=1)
	today = datetime.combine(date.today(), time.min ) #datetime( now.year, now.month, now.day )
	since = today - timedelta(days=7) - fail_offset
	now = since
	data = []
	i = 1
	while now < datetime.now() - fail_offset:
		data.append( s.query( Result.id ).filter( Result.player_id == playerid).filter( Result.date < now + inc ).filter( Result.date >= now ).count() )
		i += 1
		now += inc
	fn = 'images/plots/player_matches_%i.png'%int(playerid)
	with mutex:
		f = plt.figure(1)
		plt.plot(range(len(data)),data)
		plt.ylabel('matches per day')
		plt.xlabel('days past')
		plt.savefig(config['base_dir']+fn,transparent=True)
		plt.close(1)
	s.close()
	return config['base_url'] + fn
