#!/usr/bin/env python
# -*- coding: utf-8 -*-
from disqusapi import DisqusAPI

class Disqus(object):
	def __init__(self, config, cache):
		self.config = config
		self.cache = cache
		self.disqus = DisqusAPI(config['disqus_seckey'])
		# ( 1000 requests / 3600 seconds ) * functioncount
		self.expire_time = max(60,( 1000.0 / 3600.0 ) * 1.0)

	def matchdict(self):		
		@self.cache.cache('disqus_matches',expire=int(self.expire_time))
		def disqus_matches():
			return dict([ (int(x['identifiers'][0][6:]),x['posts']) for x in self.disqus.forums.listThreads(forum='springladder') if x['identifiers'][0][:5] == 'match' ])
		
		return disqus_matches()
		