#!/usr/bin/env python

import sys
from ranking import GlobalRankingAlgoSelector
from match import AutomaticMatchToDbWrapper
import tasbot
from ladderdb import LadderDB
files = sys.argv[1:]


import ConfigParser

from pyparsing import (Literal, CaselessLiteral, Word, Upcase, OneOrMore, ZeroOrMore, 
        Forward, NotAny, delimitedList, oneOf, Group, Optional, Combine, alphas, nums, 
        restOfLine, cStyleComment, alphanums, printables, empty, quotedString, 
        ParseException, ParseResults, Keyword, Dict )
import pprint

def parseScript(script):
	lbrace = Literal("{").suppress()
	rbrace = Literal("}").suppress()
	lbrack = Literal("[").suppress()
	rbrack = Literal("]").suppress()
	equals = Literal("=").suppress()
	semi   = Literal(";").suppress()
	comment = semi + Optional( restOfLine )
	nonrbrack = "".join( [ c for c in printables if c != "]" ] ) + " \t"
	nonequals = "".join( [ c for c in printables if c != "=" ] ) + " \t"
	
	sectionDef = lbrack + Word( nonrbrack ) + rbrack 
	keyDef = ~lbrack + Word( nonequals ) + equals 
	sectionBegin = lbrace 
	sectionEnd = rbrace 
	section = sectionDef + sectionBegin + Dict( ZeroOrMore( Group( keyDef ) ) ) + sectionEnd
	# using Dict will allow retrieval of named data fields as attributes of the parsed results
#	inibnf = Dict( ZeroOrMore( Group( section ) ) )
	inibnf = Dict( ZeroOrMore( Group( sectionDef + Dict( ZeroOrMore( Group( keyDef ) ) ) ) ) )
	inibnf.ignore( comment )
	
	iniData = "".join( open('okk').readlines() )
	return inibnf.parseString( iniData )
	
pp = pprint.PrettyPrinter(4)

tokens = parseScript('okk')
#pp.pprint( tokens.asList() )

configfile = 'Main.conf'
config = tasbot.config.Config(configfile)
tasbot.customlog.Log.init(config.get('tasbot', 'logfile', 'ladderbot.log'),
		config.get('tasbot', 'loglevel', 'info'), True )
app = tasbot.DefaultApp(configfile,'/tmp/demo.pid',False,True)
db = LadderDB( app.config.get('tasbot', "alchemy-uri"), app.admins, 
			int(app.config.get('tasbot', "alchemy-verbose")) )

lid = 1
if not db.LadderExists(lid):
#	id = GlobalRankingAlgoSelector.available_ranking_algos['TrueskillRankAlgo']
	lid = db.AddLadder('anything goes', 2 )
	
for fn in files:
	with open(fn,'r') as f:
		mr = AutomaticMatchToDbWrapper(fn, lid)			
		db.ReportMatch(mr, False)#false skips validation check of output against ladder rules
		upd = GlobalRankingAlgoSelector.GetPrintableRepresentation( db.GetRanks( lid ), db )
		print(upd)
		db.RecalcRankings(lid)
