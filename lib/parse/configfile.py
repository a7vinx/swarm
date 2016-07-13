#!/user/bin/python
# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser
from lib.core.exception import SwarmUseException

def configfile_parse(args,config_file='swarm.conf'):
	try:
		conf_parser=ConfigParser()
		conf_parser.read(config_file)

		# output options
		args.logfile=conf_parser.get('Output','logfile')
		args.verbose=conf_parser.getboolean('Output','verbose')
		args.disable_col=conf_parser.getboolean('Output','disable_col')

		# target options
		args.target=conf_parser.get('Target','target')
		args.target_file=conf_parser.get('Target','target_file')
		if args.target!='':
			args.target=args.target.split()

		# swarm options
		args.swarm=conf_parser.get('Swarm','swarm')
		args.swarm_file=conf_parser.get('Swarm','swarm_file')
		args.timeout=conf_parser.getfloat('Swarm','timeout')
		args.waken_cmd=conf_parser.get('Swarm','waken_cmd')
		args.m_addr=conf_parser.get('Swarm','m_addr')
		args.m_port=conf_parser.getint('Swarm','m_port')
		args.s_port=conf_parser.getint('Swarm','s_port')
		args.authkey=conf_parser.get('Swarm','authkey')
		args.sync_data=conf_parser.getboolean('Swarm','sync_data')
		if args.swarm!='':
			args.swarm=args.swarm.split()

		# common options
		args.process_num=conf_parser.getint('Common','process_num')
		args.thread_num=conf_parser.getint('Common','thread_num')
		args.task_granularity=conf_parser.getint('Common','task_granularity')

		# domain scan options
		args.enable_domain_scan=conf_parser.getboolean('Domain Scan','enable_domain_scan')
		args.domain_compbrute=conf_parser.getboolean('Domain Scan','domain_compbrute')
		args.domain_dict=conf_parser.get('Domain Scan','domain_dict')
		args.domain_maxlevel=conf_parser.getint('Domain Scan','domain_maxlevel')
		args.domain_charset=conf_parser.get('Domain Scan','domain_charset')
		args.domain_levellen=conf_parser.get('Domain Scan','domain_levellen')
		args.domain_timeout=conf_parser.getfloat('Domain Scan','domain_timeout')

		# directory and file scan options
		args.enable_dir_scan=conf_parser.getboolean('Directory Scan','enable_dir_scan')
		args.dir_enable_crawler=conf_parser.getboolean('Directory Scan','dir_enable_crawler')
		args.dir_enable_brute=conf_parser.getboolean('Directory Scan','dir_enable_brute')
		args.dir_crawl_seed=conf_parser.get('Directory Scan','dir_crawl_seed')
		args.dir_http_port=conf_parser.get('Directory Scan','dir_http_port')
		args.dir_https_port=conf_parser.get('Directory Scan','dir_https_port')
		args.dir_compbrute=conf_parser.getboolean('Directory Scan','dir_compbrute')
		args.dir_charset=conf_parser.get('Directory Scan','dir_charset')
		args.dir_len=conf_parser.get('Directory Scan','dir_len')
		args.dir_dict=conf_parser.get('Directory Scan','dir_dict')
		args.dir_max_depth=conf_parser.getint('Directory Scan','dir_max_depth')
		args.dir_timeout=conf_parser.getint('Directory Scan','dir_timeout')
		args.dir_not_exist=conf_parser.get('Directory Scan','dir_not_exist')
		args.dir_quick_scan=conf_parser.getboolean('Directory Scan','dir_quick_scan')

		# host scan options
		args.enable_host_scan=conf_parser.getboolean('Host Scan','enable_host_scan')

		# web vulnerabilities scan options
		args.enable_web_vul_scan=conf_parser.getboolean('Web Vul Scan','enable_web_vul_scan')

	except Exception,e:
		print 'parse config file error :'+repr(e)
		raise SwarmUseException('parse config file error'+repr(e))

