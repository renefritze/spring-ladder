#!/usr/bin/env python
# -*- coding: utf-8 -*-
from disqusapi import DisqusAPI,APIError

from tasbot.customlog import Log

class Disqus(object):
	def __init__(self, config, cache):
		self.config = config
		self._cache = cache
		self.forum = config.get('ladder','disqus_forum')
		self._disqus = DisqusAPI(config.get('ladder','disqus_seckey'),
							public_key=config.get('ladder','disqus_pubkey') )
		# ( 1000 requests / 3600 seconds ) * functioncount
		self.expire_time = max(60,( 1000.0 / 3600.0 ) * 1.0)

	def matchdict(self):		
		@self._cache.cache('disqus_matches',expire=int(self.expire_time))
		def disqus_matches():
			try:
				return dict([ (int(x['identifiers'][0][6:]),x['posts']) for x in self._disqus.forums.listThreads(forum=self.forum) if x['identifiers'][0][:5] == 'match' ])
			except APIError,a: 
				if str(a.code) != '5':
					raise a
				else:
					Log.error('Invalid disqus api-keys')
		
		return disqus_matches()
		
