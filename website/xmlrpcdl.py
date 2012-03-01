from xmlrpclib import ServerProxy
import urllib
import os
import Image 

from db_entities import Map
import globe
import myutils
import threading

class DownloadQueue(object):
	def __init__(self):
		self._proxy = ServerProxy('http://api.springfiles.com/xmlrpc.php', verbose=False)
		
	def _searchstring(self, pattern, category='Spring Maps'):
		return {
			#	"category" : "Spring Maps",
				"logical" : "or",
				"filename" : pattern,
				"springname" : pattern,
				"torrent" : False,
				"images": True,
				"metadata": True,
				"nosensitive": True,
			}
	def add_map(self,mapname):
		pattern = self._searchstring(mapname)
		result = self._proxy.springfiles.search(pattern)[0]
		name = result['name']
		nmap = Map()
		meta = result['metadata']
		nmap.startpos = [(f['x'],f['z']) for f in meta['StartPos'] ]
		nmap.name = name
		nmap.md5 = result['md5']
		try:
			imgurl = result['mapimages'][0]
			basedir = nmap.basedir(globe.config)
			basename = nmap.name + imgurl[-4:]
			local_fn = os.path.join( basedir, '1024', basename )
			globe.mkdir_p(local_fn)
			urllib.urlretrieve (imgurl, local_fn)
			img = Image.open(local_fn)
			for i in [128,256,512]:
				resized_img = img.resize((i, i), Image.ANTIALIAS)
				fn = os.path.join(basedir, str(i), basename)
				myutils.mkdir_p(fn)
				resized_img.save(fn)
			nmap.minimap = basename
		except Exception, e:
			globe.Log.exception(e)
			globe.Log.error('download for map %s failed'%nmap.name)
		nmap.height = meta['Height']
		nmap.width = meta['Width']
		return nmap
	
#	def add_map(self,mapname):
#		t = threading.Timer(1, self._download,[mapname])
#		t.start()
