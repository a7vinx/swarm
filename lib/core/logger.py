#!/user/bin/python
# -*- coding: utf-8 -*-

import logging
import sys

LOG=logging.getLogger("swarm")

def init_logger(logfile,verbose):

	file_logger = logging.FileHandler(logfile)
	cli_logger = logging.StreamHandler(sys.stdout)
	
	if verbose==True:
		LOG.setLevel(logging.DEBUG)	
	else:
		LOG.setLevel(logging.WARNING)

	formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] [in func:%(funcName)s] %(levelname)s %(message)s',
			datefmt='%d %b %Y %H:%M:%S')
	file_logger.setFormatter(formatter)
	cli_logger.setFormatter(formatter)

	LOG.addHandler(file_logger)
	LOG.addHandler(cli_logger)

	LOG.debug("logger init completed")

