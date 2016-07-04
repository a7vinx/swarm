#!/user/bin/python
# -*- coding: utf-8 -*-
import argparse
from lib.core.exception import SwarmUseException

def cli_parse(args):
	parser=argparse.ArgumentParser()

	# output option
	output=parser.add_argument_group('Output',
		'These option can be used to control output')
	output.add_argument('-v',dest='verbose',action='store_true',
			default=False,help='Output more verbose')
	output.add_argument('-c',dest='disable_col',action='store_true',
			default=False,help='Disable colorful log output')
	output.add_argument('-o',dest='logfile',metavar='PATH',
			help='Record log in target file')

	# target option
	target=parser.add_argument_group('Target',
		'At least one of these options has to be provided to define target')
	target.add_argument('-t',dest='target',metavar='TARGET',nargs='*',
			help='Target separated by blank (eg: github.com 127.0.0.0/24 192.168.1.5)')
	target.add_argument('-T',dest='target_file',metavar='PATH',
			help='File that contains target list, one target per line')

	# swarm option
	swarm=parser.add_argument_group('Swarm',
		'At least one of these options has to be provided to define slave host')
	swarm.add_argument('-s',dest='swarm',metavar='SWARM',nargs='*',
			help='Address of slave hosts with port if you need waken them'
				' (eg: 192.168.1.2:9090 192.18.1.3:9191). '
				'No port if swarm-s on slave host has already run and '
				'\'--waken\' should be empty meanwhile')
	swarm.add_argument('-S',dest='swarm_file',metavar='PATH',
			help='File that contains slave list, one host per line')
	swarm.add_argument('--waken',dest='waken_cmd',metavar='CMD',
			help='Command to waken up slave hosts, null if swarm-s on slave host has already run')
	swarm.add_argument('--timeout',dest='timeout',metavar='TIME',type=float,
			help='Seconds to wait before request to swarm getting response')
	swarm.add_argument('--m-addr',dest='m_addr',metavar='ADDR',
			help='Master address which should be reachable by all slave hosts')
	swarm.add_argument('--m-port',dest='m_port',metavar='PORT',type=int,
			help='Listen port on master host to distribute task')
	swarm.add_argument('--s-port',dest='s_port',metavar='PORT',type=int,
			help='Listen port on slave host to receive command from master')
	swarm.add_argument('--authkey',dest='authkey',metavar='KEY',
			help='Auth key between master and slave hosts')
	# swarm.add_argument('--sync',dest='sync_data',action='store_true',default=False,
	# 		help='Synchronize data like dictionary and vulnerability database etc')

	# common option
	common=parser.add_argument_group('Common',
		'These option can be used to customize common configuration of slave host')
	common.add_argument('--process',dest='process_num',metavar='NUM',type=int,
			help='Number of process running on slave host')
	common.add_argument('--thread',dest='thread_num',metavar='NUM',type=int,
			help='Number of threads running on slave host')

	# domain scan option
	domain_scan=parser.add_argument_group('Domain Scan',
		'Thes option can be used to customize swarm action of subdomain name scan')
	domain_scan.add_argument('-d',dest='enable_domain_scan',action='store_true',default=False,
			help='Do subdomain scan on target')
	domain_scan.add_argument('--d-compbrute',dest='domain_compbrute',action='store_true',default=False,
			help='Use complete brute force without dictionary on target')
	domain_scan.add_argument('--d-dict',dest='domain_dict',metavar='PATH',
			help='Path to dictionary used for subdomain name scan')
	domain_scan.add_argument('--d-maxlevel',dest='domain_maxlevel',metavar='NUM',
			help='Max level of subdomain name to scan')
	domain_scan.add_argument('--d-charset',dest='domain_charset',metavar='SET',
			help='Charset used for complete brute foce')
	domain_scan.add_argument('--d-levellen',dest='domain_levellen',metavar='LEN',
			help='Length interval of subdomain name each level')
	domain_scan.add_argument('--d-timeout',dest='domain_timeout',metavar='TIME',type=float,
			help='Timeout option for subdomain name scan')


	parser.parse_args(namespace=args)

	if not any((args.target,args.target_file)):
		print 'At least one target need to be provided'
		raise SwarmUseException('At least one target need to be provided')

	if not any((args.swarm,args.swarm_file)):
		print 'At least one swarm need to be provided'
		raise SwarmUseException('At least one swarm need to be provided')

