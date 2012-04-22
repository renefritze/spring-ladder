#!/usr/bin/env python
import sys
import os
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
	
	
if __name__ == "__main__":
	pp = pprint.PrettyPrinter(4)
