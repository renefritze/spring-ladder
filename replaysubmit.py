import os
import platform
if platform.system() == "Windows":
	import win32api

from tasbot.customlog import Log

from match import AutomaticMatchToDbWrapper, UnterminatedReplayException


class ReplayReporter(object):
	def  __init__ (self, db, config):
		self.db = db
		self.config = config

	def SubmitLadderReplay( self, replaypath, ladderid, do_validation=True ):
		try:
			if not self.db.LadderExists( ladderid ):
				Log.error( "Error: ladder %d does not exist" % ( ladderid ) )
				return False
			else:
				try:
					open(replaypath).close()
					mr = AutomaticMatchToDbWrapper(replaypath, ladderid, self.config, self.db)
					return self.db.ReportMatch( mr, do_validation )
				except UnterminatedReplayException:
					Log.error('skipping unterminated replay %s'%replaypath, 'ReplayReporter')
				except Exception,e:
					Log.error('reporting match failed', 'ReplayReporter')
					Log.exception(e)
				return False
		except Exception, e:
			Log.exception(e)
			return False
		return True
