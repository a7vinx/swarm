#!/user/bin/python
# -*- coding: utf-8 -*-

import logging
import sys

LOG=logging.getLogger("swarm")

def init_logger(logfile,verbose,disable_col):

	file_logger = logging.FileHandler(logfile)
	
	if disable_col==False:
		try:
			from thirdparty.ansistrm.ansistrm import ColorizingStreamHandler
			cli_logger = ColorizingStreamHandler(sys.stdout)
			cli_logger.level_map[logging.DEBUG]=(None, 'white', False)
			cli_logger.level_map[logging.INFO]=(None, 'green', False)
		except ImportError:
			print 'import error'
			cli_logger = logging.StreamHandler(sys.stdout)
	else:
		cli_logger=logging.StreamHandler(sys.stdout)
	
	if verbose==True:
		LOG.setLevel(logging.DEBUG)	
	else:
		LOG.setLevel(logging.WARNING)

	file_formatter = logging.Formatter('[%(asctime)s] %(filename)s[line:%(lineno)d] [in func:%(funcName)s] %(levelname)s %(message)s',
			datefmt='%d %b %Y %H:%M:%S')
	cli_formatter = logging.Formatter('[%(asctime)s] %(filename)s[line:%(lineno)d] [in func:%(funcName)s] %(levelname)s %(message)s',
			datefmt='%H:%M:%S')
	file_logger.setFormatter(file_formatter)
	cli_logger.setFormatter(cli_formatter)

	LOG.addHandler(file_logger)
	LOG.addHandler(cli_logger)

	LOG.debug("logger init completed")

