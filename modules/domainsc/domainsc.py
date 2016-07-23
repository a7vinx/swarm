#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import copy
from multiprocessing.dummy import Pool
from multiprocessing import TimeoutError
from lib.utils.brute import generate_bflist
from lib.core.logger import LOG
from lib.parse.host import removeip
from lib.utils.subtasks import generate_compbrute_subtask
from lib.utils.subtasks import generate_dictbrute_subtask
from lib.core.exception import SwarmParseException
from lib.core.exception import SwarmUseException

def add_cli_args(cli_parser):
	# domain scan options
	domain_scan=cli_parser.add_argument_group('Domain Scan',
		'Thes option can be used to customize swarm action of subdomain name scan')
	domain_scan.add_argument('--dom-compbrute',dest='domain_compbrute',action='store_true',
			help='Use complete brute force without dictionary on target')
	domain_scan.add_argument('--dom-dict',dest='domain_dict',metavar='PATH',
			help='Path to dictionary used for subdomain name scan')
	domain_scan.add_argument('--dom-maxlevel',dest='domain_maxlevel',metavar='NUM',
			help='Max level of subdomain name to scan')
	domain_scan.add_argument('--dom-charset',dest='domain_charset',metavar='SET',
			help='Charset used for complete brute foce')
	domain_scan.add_argument('--dom-levellen',dest='domain_levellen',metavar='LEN',
			help='Length interval of subdomain name each level')
	domain_scan.add_argument('--dom-timeout',dest='domain_timeout',metavar='TIME',type=float,
			help='Timeout option for subdomain name scan')

def parse_conf(args,conf_parser):
	# domain scan options
	args.domain_compbrute=conf_parser.getboolean('Domain Scan','domain_compbrute')
	args.domain_dict=conf_parser.get('Domain Scan','domain_dict')
	args.domain_maxlevel=conf_parser.getint('Domain Scan','domain_maxlevel')
	args.domain_charset=conf_parser.get('Domain Scan','domain_charset')
	args.domain_levellen=conf_parser.get('Domain Scan','domain_levellen')
	args.domain_timeout=conf_parser.getfloat('Domain Scan','domain_timeout')


class Master(object):
	"""
	Subdomain name task distributor and task result handler.

	Use a dict with domain name as keys and a list contains subdomain names as values
	to store result get from swarm.
	For example:

	{'github.com':['gist.github.com','XX.github.com'],
	 'stackoverflow.com':['XX.stackoverflow.com',]} 

	Task Format:
		Task:
		domain name|dict|dict_path|start_line|scan_lines
		domain name|comp|charset|begin_str|end_str
		Result:
		subdomain name;subdomain name;subdomain name
		no subdomain
	Example:
		put task:
		github.com|dict|./dictionary/domain.dict|2000|3000
		github.com|comp|ABCDEFGHIJKLMN8980|DAAA|D000
		get result:
		gist.github.com;XX.github.com
		no subdomain
	"""
	def __init__(self, args):
		super(Master, self).__init__()
		self._args = args
		self._domain_list=removeip(self._args.target_list)
		# copy it for quick query 
		self._domain_list_orig=copy.copy(self._domain_list)
		# do some check
		if len(self._domain_list)==0:
			raise SwarmUseException('domain name must be provided')			
		if self._args.domain_maxlevel<=0:
			raise SwarmUseException('subdomain name max level must be positive')

		# initial the collection
		self._args.coll.insert({'root':self._domain_list})
		# record current subdomain name level
		self._curlevel=0

	def generate_subtasks(self):
		"""
		Decomposition domain name scan task and distribute tasks, get result from swarm.
		Task granularity should not be too small or too huge.
		"""	
		self._curlevel+=1
		# if it is out of range, end this task
		if self._curlevel>self._args.domain_maxlevel:
			return []

		# begin to discomposition 
		if self._args.domain_compbrute==True:				
			try:
				# generate list of subtasks
				subtasklist=generate_compbrute_subtask(self._domain_list,self._args.domain_levellen,
					self._args.domain_charset,self._args.task_granularity)
			except SwarmParseException as e:
				raise SwarmUseException('invalid subdomain name '+str(e)+', or format error')
		# use dictionary 
		else:
			if self._args.domain_dict=='':
				raise SwarmUseException('domain name dictionary need to be provided')

			try:
				# generate list of subtasks
				subtasklist=generate_dictbrute_subtask(self._domain_list,self._args.domain_dict,
					self._args.task_granularity)
			except IOError as e:
				raise SwarmUseException('can not open dictionary for domain scan, path:%s'%(dict))	
		# clear domain list for next iteration
		self._domain_list=[]
		return subtasklist	

	def handle_result(self,result):	
		if result!='no subdomain':
			resultl=result.split(';')
			# update domain name list for next iteration
			self._domain_list.extend(resultl)
			# add it into scan result meanwhile
			for curkey in self._domain_list_orig:
				if resultl[0].find(curkey)==len(resultl[0])-len(curkey):
					self._args.coll.insert({'domain':curkey,'subdomain':resultl})
					break

	def report(self):
		for curdomain in self._domain_list_orig:
			all_subdomain=[]
			subdomain=self._args.coll.find({'domain':curdomain})
			for cursub in subdomain:
				all_subdomain.extend(cursub['subdomain'])
			print '============= scan result of '+curdomain+' =============='
			print '\n'.join(all_subdomain)
		print '========================================================='
		

class Slave(object):
	"""
	Subdomain name scanner providing functions of complete brute force and dictionary 
	brute force.

	Task Format:
		Task:
		domain name|dict|dict_path|start_line|scan_lines
		domain name|comp|charset|begin_str|end_str
		Result:
		subdomain name;subdomain name;subdomain name
		no subdomain
	Example:
		put task:
		github.com|dict|./dictionary/domain.dict|2000|3000
		github.com|comp|ABCDEFGHIJKLMN8980|DAAA|D000
		get result:
		gist.github.com;XX.github.com
		no subdomain
	"""
	def __init__(self, args):
		super(Slave, self).__init__()
		self._pool=Pool(args.thread_num)
		self._timeout=args.domain_timeout
		
	def do_task(self,task):
		task=task.split('|')
		if task[1]=='dict':
			result=self.dict_brute(task[0],task[2],task[3],task[4])
		else:
			result=self.complete_brute(task[0],task[2],task[3],task[4])
		return result

	def complete_brute(self,target,charset,begin_str,end_str):
		resultl=[]
		bflist=generate_bflist(charset,begin_str,end_str)
		for cur in bflist:
			cur_target=cur+'.'+target
			resultl.append(self._pool.apply_async(self._scan_target,args=(cur_target,)))
		return self._get_result(resultl)

	def dict_brute(self,target,dict_path,start_line,lines):
		resultl=[]
		lines=int(lines,10)
		start_line=int(start_line,10)
		with open(dict_path) as fp:
			fcontent=fp.readlines()
			for cur_index in range(lines):
				cur_target=fcontent[start_line+cur_index-1].strip()+'.'+target
				resultl.append(self._pool.apply_async(self._scan_target,args=(cur_target,)))
		return self._get_result(resultl)

	def _get_result(self,resultl):
		result=''
		# get result from list
		for cur in resultl:
			try:
				result+=cur.get(timeout=self._timeout)
			except TimeoutError as e:
				continue
		# deal with result
		if result=='':
			result='no subdomain'
		else:
			result=result[:-1]
		return result
				
	def _scan_target(self,target):
		try:
			LOG.debug('scan target: %s'%target)
			socket.getaddrinfo(target,None)
			return target+';'
		except Exception as e:
			return ''

	