#!/user/bin/python
# -*- coding: utf-8 -*-

import argparse
from socket import timeout

from lib.parse.configfile import configfile_parse
from lib.parse.cli import cli_parse
from lib.core.logger import LOG
from lib.core.logger import init_logger
from lib.core.mswarm import MSwarm
from lib.core.exception import SwarmBaseException

def main():
		
	args=argparse.Namespace()
	try:
		configfile_parse(args)
		cli_parse(args)
		init_logger(args.logfile,args.verbose,args.disable_col)

		m=MSwarm(args)
		# wake slaves up
		m.waken_swarm()
		m.parse_distribute_task()

	except SwarmBaseException, e:
		return

	

if __name__ == '__main__':
	main()