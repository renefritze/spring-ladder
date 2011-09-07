# -*- coding: utf-8 -*-
from customlog import *
from ParseConfig import *
import commands
import thread
import signal
import os
import time
import subprocess
import traceback
import platform
import sys

from db_entities import *
from ladderdb import *
from match import *

if platform.system() == "Windows":
	import win32api

from utilities import *

class ReplayReporter:
	def  __init__ ( alchemyuri, alchemyverbose, springdedclientpath, springdatapath ):
		self.springdedclientpath = springdedclientpath
		self.springdatapath = springdatapath
		db = LadderDB( alchemyuri, alchemyverbose )

	def SubmitLadderReplay( replaypath, ladderid ):
		currentworkingdir = os.getcwd()
		try:
			output = ""
			doSubmit = ladderid != -1 and db.LadderExists( ladderid )
			if not doSubmit:
				Log.error( red + "Error: ladder %d does not exist" % ( ladderid ) + normal, 'ReplayReporter' )
				return False
			st = time.time()
			Log.info( "*** Starting spring: command line \"%s %s\"" % (self.springdedclientpath, replaypath ), 'ReplayReporter' ) 
			if platform.system() == "Windows":
				dedpath = "\\".join(self.springdedclientpath.replace("/","\\").split("\\")[:self.springdedclientpath.replace("/","\\").count("\\")])
				if not dedpath in sys.path:
					sys.path.append(dedpath)
			if self.springdatapath != None:
				if not self.springdatapath in sys.path:
					sys.path.append(self.springdatapath)
				os.chdir(self.springdatapath)
				os.environ['SPRING_DATADIR'] = self.springdatapath
			pr = subprocess.Popen( (self.springdedclientpath, replaypath ),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,cwd=self.springdatapath )
			l = pr.stdout.readline()
			while len(l) > 0:
				output += l
				l = pr.stdout.readline()
			status = pr.wait()
			et = time.time()
			Log.info(  "*** Spring has exited with status %i" % status, 'ReplayReporter' )
			if status != 0:
				Log.error( output, 'ReplayReporter' )
			elif doSubmit:
				mr = MatchToDbWrapper( output, ladderid )
				try:
					db.ReportMatch( mr )
				except Exception:
					Log.error( 'reporting match failed', 'ReplayReporter' )
					return False
		except Exception:
			exc = traceback.format_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
			Log.error( "*** EXCEPTION: BEGIN\n%s\nEXCEPTION: END"%exc, 'ReplayReporter' )
			os.chdir(currentworkingdir)
			return False
		os.chdir(currentworkingdir)
		return True
