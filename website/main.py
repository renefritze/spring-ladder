#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bottle import route, run, debug, PasteServer, static_file, redirect, abort, request, default_app
import os, index, viewmatch, viewplayer, viewladder, viewrules, \
	help, fame, scoreboard, change_ladder,adminindex, recalc, deleteladder, \
	adminmatch, feeds, viewmap
from globe import config,staging,local_file


pp = os.path.join(config.get('ladder','base_dir'),'images')
print pp

@route('/static/:filename')
def static_files(filename):
	return static_file( filename, root=os.getcwd()+'/static/' )
@route('/images/<filename:path>')
def image_file(filename):
	return send_file( filename, 'images')
@route('/images/plots/:filename')
def image_file2(filename):
	return static_file( filename, root=os.getcwd()+'/images/plots/' )
	
@route('/demos/:filename')
def demos(filename):
	return static_file( filename, root=os.getcwd()+'/demos/' )

@route('/favicon.ico')
def favi():
	return static_file( 'favicon.ico', root=os.getcwd()+'/images/' )

if __name__=="__main__":
	port = int(config.get('ladder','port'))
	debug(True)
	app = default_app()
	run(app=app,server=PasteServer,host='localhost',port=port , reloader=False)
