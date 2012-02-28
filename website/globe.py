# -*- coding: utf-8 -*-
from jinja2 import Environment, FileSystemLoader
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
import os 
import errno
from tasbot.customlog import Log
from tasbot.config import Config

from disqus import Disqus
from ladderdb import LadderDB


def mkdir_p(path):
	path = os.path.dirname(path)
	try:
		os.makedirs(path)
	except OSError as exc: # Python >2.5
		if exc.errno == errno.EEXIST:
			pass
		else: raise
		
cache_opts = {
    'cache.type': 'memory',
    'cache.data_dir': 'tmp/cache/data',
    'cache.lock_dir': 'tmp/cache/lock'
}

config = Config( 'Main.conf' )
Log.init( 'website.log' )
db = LadderDB(config.get('tasbot','alchemy-uri'))
env = Environment(loader=FileSystemLoader('templates'))
staging = config.get_bool('tasbot','staging')
cache = CacheManager(**parse_cache_config_options(cache_opts))
discus = Disqus(config,cache)
mkdir_p(config.get('ladder','base_dir'))