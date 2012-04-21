#!/usr/bin/env python
import ConfigParser
import sys
import os
from pyparsing import (Literal, CaselessLiteral, Word, Upcase, OneOrMore, ZeroOrMore, 
        Forward, NotAny, delimitedList, oneOf, Group, Optional, Combine, alphas, nums, 
        restOfLine, cStyleComment, alphanums, printables, empty, quotedString, 
        ParseException, ParseResults, Keyword, Dict )
import pprint


import tasbot
from ladderdb import LadderDB
from replaysubmit import ReplayReporter


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
	
	
if __name__ == "__main__":
	pp = pprint.PrettyPrinter(4)
	configfile = 'Main.conf'
	config = tasbot.config.Config(configfile)
	tasbot.customlog.Log.init( 'import.log' )
	admins = config.get_optionlist('tasbot', "admins")
	db = LadderDB(config.get('tasbot', "alchemy-uri"), admins, 
				int(config.get('tasbot', "alchemy-verbose")) )
	lid = 1
	if not db.LadderExists(lid):
		lid = db.AddLadder('anything goes', 2 )
	
	files = sys.argv[1:]
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
