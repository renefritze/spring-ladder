from bottle import route,request

from fieldsets import *
from ladderdb import ElementNotFoundException
from ranking import EmptyRankingListException
from db_entities import Roles, Result, Option, Bans, GlickoRanks, SimpleRanks, TrueskillRanks, MatchSetting, Match
from globe import db,env
from auth import AuthDecorator

@route('/admin/deleteladder', method='GET')
@AuthDecorator( Roles.GlobalAdmin, db )
def output( ):

	user = request.player
	try:
		id = getSingleField( 'id', request, getSingleFieldPOST('id', request )  )
		lad = db.GetLadder( id )
		if not db.AccessCheck( id, request.player.nick, Roles.GlobalAdmin ):
			template = env.get_template('error.html')
			return template.render( err_msg="you're not allowed to delete ladder #%s"%(str(id)) )
		ask = True
		if getSingleField( 'confirm', request  ) == 'yes':
			session = db.sessionmaker()
			#figure out proper delete cascade instead
			SYNC_STRAT = 'fetch'
			session.query( Result ).filter( Result.ladder_id == id ).delete(synchronize_session=SYNC_STRAT)
			session.query( Option ).filter( Option.ladder_id == id ).delete(synchronize_session=SYNC_STRAT)
			session.query( Bans ).filter( Bans.ladder_id == id ).delete(synchronize_session=SYNC_STRAT)
			session.query( GlickoRanks ).filter( GlickoRanks.ladder_id == id ).delete(synchronize_session=SYNC_STRAT)
			session.query( SimpleRanks ).filter( SimpleRanks.ladder_id == id ).delete(synchronize_session=SYNC_STRAT)
			session.query( TrueskillRanks ).filter( TrueskillRanks.ladder_id == id ).delete(synchronize_session=SYNC_STRAT)
			matches = session.query( Match.id ).filter( Match.ladder_id == id )
			session.query( MatchSetting ).filter( MatchSetting.match_id.in_(matches) ).delete(synchronize_session=SYNC_STRAT)
			matches.delete()
			session.delete( lad )
			session.commit()
			session.close()
			ask = False
		template = env.get_template('deleteladder.html')
		return template.render( ladder=lad, ask=ask )

	except ElementNotFoundException, e:
		err = str(e)

	except Exception, f:
		err = str(f)

	template = env.get_template('error.html')
	return template.render( err_msg=err )
