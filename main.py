#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys


from tasbot.customlog import Log

if __name__=="__main__":
	tasbot.check_min_version((1,))
	r = False
	for arg in sys.argv:
		if arg.strip() == "-r":
			r = True
			Log.Notice("Registering account")
	slave = False
	try:
		idx = sys.argv.index('-c')
		configfile = sys.argv[idx+1]
		slave = True
	except Exception,e:
		configfile = "Main.conf"
	print('using configfile %s'%configfile)

	config = tasbot.config.Config(configfile)
	Log.init(config.get('tasbot', 'logfile', 'ladderbot.log'),
			 config.get('tasbot', 'loglevel', 'info'), True )
	if slave:
		pidfile = config.get('tasbot','pidfile','ladderbot.pid')
	else:
		pidfile = config.get('tasbot','pidfile','ladderbot.pid2')
	print 'using pidfile %s'%pidfile
	inst = tasbot.DefaultApp(configfile,pidfile,r,True)
	if slave or bool(config.GetSingleOption( 'tasbot','debug', False )):
		inst.run()#exec in fg
	else:
		inst.start()
