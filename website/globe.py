# -*- coding: utf-8 -*-
from jinja2 import Environment, FileSystemLoader
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

from tasbot.customlog import Log
from tasbot.config import Config

from disqus import Disqus
import ladderdb 
from myutils import mkdir_p

		
cache_opts = {
    'cache.type': 'memory',
    'cache.data_dir': 'tmp/cache/data',
    'cache.lock_dir': 'tmp/cache/lock'
}

config = Config( 'Main.conf' )
Log.init( 'website.log' )
db = ladderdb.LadderDB(config.get('tasbot','alchemy-uri'))
env = Environment(loader=FileSystemLoader('templates'))
staging = config.get_bool('tasbot','staging')
cache = CacheManager(**parse_cache_config_options(cache_opts))
disqus = Disqus(config,cache)
mkdir_p(config.get('ladder','base_dir'))

def local_file(filename, sub, **kwargs):
	path = os.path.join(config.get('ladder','base_dir'),sub) 
	Log.error(path)
	return static_file(filename, root=path)
