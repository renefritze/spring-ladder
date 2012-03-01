from bottle import route,request

from globe import db,env
from fieldsets import getSingleField
from db_entities import Map
from ladderdb import ElementNotFoundException

@route('/maplist')
def output( ):
	limit = int(getSingleField( 'limit', request, 18 ))
	try:
		s = db.sessionmaker()
		template = env.get_template('viewmaplist.html')
		if limit > -1:
			maps = s.query( Map ).order_by(Map.name.desc()).limit(limit).all()
		else:
			maps = s.query( Map ).order_by(Map.name.desc()).all()
		ret = template.render( maps=maps, limit=limit )
		s.close()
		return ret
		
	except ElementNotFoundException, e:
		err_msg="map with id %s not found"%(str(id))

	if s:
		s.close()
	template = env.get_template('error.html')
	return template.render( err_msg=err_msg )