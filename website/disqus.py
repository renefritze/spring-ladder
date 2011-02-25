#!/usr/bin/env python
# -*- coding: utf-8 -*-
from disqusapi import DisqusAPI

class Disqus(object):
	def __init__(self, config, cache):
		self.config = config
		self.cache = cache
		self.disqus = DisqusAPI(config['disqus_seckey'])

	def matchdict(self):
		
		def disqus_matches():
			print 'not cached@! disqus_matches():'
			 #dict([ (int(d.date.strftime('%m')),d.id) for d in links] )
			return dict([ (int(x['identifiers'][0][6:]),x['posts']) for x in self.disqus.forums.listThreads(forum='springladder') if x['identifiers'][0][:5] == 'match' ])
		
		return disqus_matches()
		