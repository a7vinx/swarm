#!/user/bin/python
# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser
from lib.core.exception import SwarmUseException

def configfile_parse(args,config_file='swarm.conf'):
	try:
		conf_parser=ConfigParser()
		conf_parser.read(config_file)

		# output options
		args.logfile=conf_parser.get("Output","logfile")
		args.verbose=conf_parser.getboolean("Output","verbose")
		args.disable_col=conf_parser.getboolean("Output","disable_col")

		# target options
		args.target=conf_parser.get("Target","target")
		args.target_file=conf_parser.get("Target","target_file")
		if args.target!='':
			args.target=args.target.split()

		# swarm options
		args.swarm=conf_parser.get("Swarm","swarm")
		args.swarm_file=conf_parser.get("Swarm","swarm_file")
		args.timeout=conf_parser.getfloat("Swarm","timeout")
		args.waken_cmd=conf_parser.get("Swarm","waken_cmd")
		args.m_addr=conf_parser.get("Swarm","m_addr")
		args.m_port=conf_parser.getint("Swarm","m_port")
		args.s_port=conf_parser.getint("Swarm","s_port")
		args.authkey=conf_parser.get("Swarm","authkey")
		args.sync_data=conf_parser.getboolean("Swarm","sync_data")
		if args.swarm!='':
			args.swarm=args.swarm.split()

		# common options
		args.process_num=conf_parser.getint("Common","process_num")
		args.thread_num=conf_parser.getint("Common","thread_num")

		# domain scan options
		args.enable_domain_scan=conf_parser.getboolean("Domain Scan","enable_domain_scan")
		args.domain_compbrute=conf_parser.getboolean("Domain Scan","domain_compbrute")
		args.domain_dict=conf_parser.get("Domain Scan","domain_dict")
		args.domain_maxlevel=conf_parser.getint("Domain Scan","domain_maxlevel")
		args.domain_charset=conf_parser.get("Domain Scan","domain_charset")
		args.domain_levellen=conf_parser.get("Domain Scan","domain_levellen")
		args.domain_timeout=conf_parser.getfloat("Domain Scan","domain_timeout")

	except Exception,e:
		print 'parse config file error :'+repr(e)
		raise SwarmUseException('parse config file error'+repr(e))

