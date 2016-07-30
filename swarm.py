#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

from lib.parse.configfile import configfile_parse
from lib.parse.cli import cli_parse
from lib.core.module import get_modules
from lib.core.logger import LOG
from lib.core.logger import init_logger
from lib.core.mswarm import MSwarm
from lib.core.exception import SwarmBaseException
from lib.utils.banner import begin_banner
from lib.utils.banner import end_banner

def main():
	args=argparse.Namespace()
	try:
		# get all available modules
		args.modules=get_modules()
		# parse args from cli and configuration file
		# arguments parsed from cli will cover origin arguments in configuration file
		configfile_parse(args)
		cli_parse(args)
		begin_banner()
		
		init_logger(args.logfile,args.verbose,args.disable_col)
	except SwarmBaseException as e:
		print str(e)
		end_banner()
		return

	# now use logger instead of simple print
	try:
		m=MSwarm(args)
		# wake slaves up now
		m.waken_swarm()
		m.parse_distribute_task()
	except SwarmBaseException as e:
		LOG.critical(str(e))
	finally:
		end_banner()

	
if __name__ == '__main__':
	main()