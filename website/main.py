#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bottle import route, run, debug, PasteServer, redirect, abort, request, default_app
import os 

import index, viewmatch, viewplayer, viewladder, viewrules, \
	help, fame, scoreboard, change_ladder,adminindex, recalc, deleteladder, \
	adminmatch, feeds, viewmap
from globe import config,staging,local_file


pp = os.path.join(config.get('ladder','base_dir'),'images')
print pp

@route('/static/:filename')
def local_files(filename):
	return local_file( filename, 'static' )
@route('/images/<filename:path>')
def image_file(filename):
	return local_file( filename, 'images')
@route('/images/plots/:filename')
def image_file2(filename):
	return local_file( filename, 'images/plots' )
	
@route('/demos/:filename')
def demos(filename):
	return local_file( filename, 'demos' )

@route('/favicon.ico')
def favi():
	return local_file( 'favicon.ico', 'images' )

if __name__=="__main__":
	port = int(config.get('ladder','port'))
	debug(True)
	app = default_app()
	run(app=app,server=PasteServer,host='localhost',port=port , reloader=False)
