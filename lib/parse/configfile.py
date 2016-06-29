#!/user/bin/python
# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser

def configfile_parse(args,config_file='swarm.conf'):
	conf_parser=ConfigParser()
	conf_parser.read(config_file)

	args.target=conf_parser.get("Target","target")
	args.target_file=conf_parser.get("Target","target_file")
	if args.target!='':
		args.target=args.target.split()


	args.swarm=conf_parser.get("Swarm Connection","swarm")
	args.swarm_file=conf_parser.get("Swarm Connection","swarm_file")
	args.timeout=conf_parser.getfloat("Swarm Connection","timeout")
	args.waken_cmd=conf_parser.get("Swarm Connection","waken_cmd")
	args.m_addr=conf_parser.get("Swarm Connection","m_addr")
	args.m_port=conf_parser.getint("Swarm Connection","m_port")
	args.s_port=conf_parser.getint("Swarm Connection","s_port")
	args.authkey=conf_parser.get("Swarm Connection","authkey")
	if args.swarm!='':
		args.swarm=args.swarm.split()

	args.logfile=conf_parser.get("Output","logfile")
	args.verbose=conf_parser.getboolean("Output","verbose")

	# args.threads=conf_parser.get("Optimization",threads)

	args.comp_brute=conf_parser.get("Brute Force","comp_brute")
	args.dict_domain=conf_parser.get("Brute Force","dict_domain")
	args.dict_dir=conf_parser.get("Brute Force","dict_dir")
