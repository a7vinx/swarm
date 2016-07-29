#!/usr/bin/env python
# -*- coding: utf-8 -*-

import importlib
import ConfigParser
from lib.core.exception import SwarmUseException
from lib.core.exception import SwarmModuleException

def configfile_parse(args):
	try:
		conf_parser=ConfigParser.ConfigParser()
		conf_parser.read('swarm.conf')

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

		# database options
		args.db_addr=conf_parser.get('Database','db_addr')
		args.db_port=conf_parser.getint('Database','db_port')

		# common options
		args.process_num=conf_parser.getint('Common','process_num')
		args.thread_num=conf_parser.getint('Common','thread_num')
		args.task_granularity=conf_parser.getint('Common','task_granularity')

		# parse arguments of modules in confiuration file	
		try:
			for curmod in args.modules:
				module=importlib.import_module('modules.'+curmod+'.'+curmod)
				conf_parser=ConfigParser.ConfigParser()
				conf_parser.read('./etc/'+curmod+'.conf')
				module.parse_conf(args,conf_parser)
		except ImportError as e:
			# print repr(e)
			raise SwarmModuleException('an error occured when try to import module: '+curmod+
				' info: '+repr(e))
		except Exception as e:
			raise SwarmModuleException('an error occured when parse configuration file of module:'+
				curmod+' info: '+repr(e))
		
	except SwarmModuleException as e:
		raise e
	except Exception as e:
		raise SwarmUseException('parse config file error: '+repr(e))

