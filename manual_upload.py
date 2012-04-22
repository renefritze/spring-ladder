#!/usr/bin/env python
import ConfigParser
import sys
import os
import pprint


import tasbot
from ladderdb import LadderDB
from replaysubmit import ReplayReporter
from db_entities import Ladder

if __name__ == "__main__":
	pp = pprint.PrettyPrinter(4)
	configfile = 'Main.conf'
	config = tasbot.config.Config(configfile)
	tasbot.customlog.Log.init( 'import.log' )
	admins = config.get_optionlist('tasbot', "admins")
	db = LadderDB(config.get('tasbot', "alchemy-uri"), admins, 
				int(config.get('tasbot', "alchemy-verbose")) )
	try:
		lid = sys.argv[1]
		lad = db.sessionmaker().query( Ladder ).filter( Ladder.id == lid ).one()
	except Exception,e:	
		tasbot.customlog.Log.exception(e)
		tasbot.customlog.Log.error('first arg needs to be a valid ladder_id')
		print('first arg needs to be a valid ladder_id')
		sys.exit(-1)

	files = sys.argv[2:]
	fails = []
	reporter = ReplayReporter(db)
	for fn in [ f for f in files if os.path.exists(f)]:
		reported = reporter.SubmitLadderReplay(fn, lid,False)
		if not reported:
			fails.append(fn)
			
	db.RecalcRankings(lid)
	if len(fails):
		print('Replays failed to parse:')
		print('\n'.join(fails))
