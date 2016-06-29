#!/user/bin/python
# -*- coding: utf-8 -*-
import argparse


def cli_parse(args):
	parser=argparse.ArgumentParser()
	target=parser.add_argument_group("Target","At least one of these options has to be provided")
	optimization=parser.add_argument_group("Optimization","Use these options to optimize the performance")
	bruteforce=parser.add_argument_group("Brute Force","Use these options to ")
	swarm=parser.add_argument_group("Swarm","")
	output=parser.add_argument_group("Output","")

	output.add_argument('-v',dest="verbose",action="store_true",
			default=False,help="output verbose")
	output.add_argument('-o',dest="logfile",metavar="=PATH",help="Record log in target file")

	# Target option
	target.add_argument("-t",dest="target",metavar="TARGET",nargs='*',
			help="Target URL, IP address or network segment, separated by blank (eg: baidu.com 127.0.0.0/24)")
	target.add_argument("-T",dest="target_file",metavar="=PATH",
			help="File that contains target list, one target per line")

	# Swarm option
	swarm.add_argument("-s",dest="swarm",metavar="SWARM",nargs='*',
			help="Slave hosts which runs sswarm to complete target task, separated by blank (eg: 127.0.0.1:13110)")
	swarm.add_argument("-S",dest="swarm_file",metavar="=PATH",
			help="File that contains slave list, one slave per line")

	# Optimization option
	# optimization.add_argument("--threads",dest="threads",metavar="=THREADS",help="Max number of concurrent threads")

	# Brute Force option
	bruteforce.add_argument("--complete-brute",dest="comp_brute",action="store_true",
			default=False,help="use complete brute force without dictionary")
	bruteforce.add_argument("--dict-domain",dest="dict_domain",metavar="=PATH",
			help="dictionary you want to use during domain scan")
	bruteforce.add_argument("--dict-dir",dest="dict_dir",metavar="=PATH",
			help="dictionary you want to use during directories and files scan")


	# other
	# parser.add_argument('-o',help="output file")

	parser.parse_args(namespace=args)

	# check args
	if not any((args.target,args.target_file)):
		print "At least one target need to be provided!\n"


