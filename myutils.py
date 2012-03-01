import os 
import errno


def mkdir_p(path):
	path = os.path.dirname(path)
	try:
		os.makedirs(path)
	except OSError as exc: # Python >2.5
		if exc.errno == errno.EEXIST:
			pass
		else: raise