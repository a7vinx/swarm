#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from multiprocessing.dummy import Pool
from multiprocessing import TimeoutError
from lib.parse.args import parse_port_list
from lib.utils.brute import generate_bflist
from lib.utils.subtasks import generate_compbrute_subtask
from lib.utils.subtasks import generate_dictbrute_subtask
from lib.core.logger import LOG
from lib.core.logger import REPORT
from lib.core.exception import SwarmUseException
from lib.core.exception import SwarmParseException


def add_cli_args(cli_parser):
	# dir scan options
	dir_scan=cli_parser.add_argument_group('Directory Scan',
		'These option can be used to customize swarm action of directory scan')
	dir_scan.add_argument('--dir-http-port',dest='dir_http_port',metavar='PORT',
			help="Separated by '|' if you need multiple ports")
	dir_scan.add_argument('--dir-https-port',dest='dir_https_port',metavar='PORT',
			help="Separated by '|' if you need multiple ports")
	dir_scan.add_argument('--dir-compbrute',dest='dir_compbrute',action='store_true',
			help='Use complete brute force without dictionary on target')
	dir_scan.add_argument('--dir-charset',dest='dir_charset',metavar='SET',
			help='Charset used for complete brute foce')
	dir_scan.add_argument('--dir-len',dest='dir_len',metavar='LEN',
			help='Length interval of directory name or file name')
	dir_scan.add_argument('--dir-dict',dest='dir_dict',metavar='PATH',
			help='Path to dictionary used for directory scan')
	dir_scan.add_argument('--dir-maxdepth',dest='dir_maxdepth',metavar='NUM',type=int,
			help='Max depth in directory and file scan')
	dir_scan.add_argument('--dir-timeout',dest='dir_timeout',metavar='TIME',type=float,
			help='Timeout option for directory scan')
	dir_scan.add_argument('--dir-not-exist',dest='dir_not_exist',metavar='FLAG',
			help="Separated by '|' if you need multiple flags")
	dir_scan.add_argument('--dir-quick-scan',dest='dir_quick_scan',action='store_true',
			help='Use HEAD method instead of GET in scan')

def parse_conf(args,conf_parser):
	# directory and file scan options
	args.dir_http_port=conf_parser.get('Directory Scan','dir_http_port')
	args.dir_https_port=conf_parser.get('Directory Scan','dir_https_port')
	args.dir_compbrute=conf_parser.getboolean('Directory Scan','dir_compbrute')
	args.dir_charset=conf_parser.get('Directory Scan','dir_charset')
	args.dir_len=conf_parser.get('Directory Scan','dir_len')
	args.dir_dict=conf_parser.get('Directory Scan','dir_dict')
	args.dir_maxdepth=conf_parser.getint('Directory Scan','dir_maxdepth')
	args.dir_timeout=conf_parser.getfloat('Directory Scan','dir_timeout')
	args.dir_not_exist=conf_parser.get('Directory Scan','dir_not_exist')
	args.dir_quick_scan=conf_parser.getboolean('Directory Scan','dir_quick_scan')

class Master(object):
	"""
	Directories and files scan task distributor and task result handler.

	Use a dict with domain name as keys and a list contains subdomain names as values to store
	scan result.
	For example:

	{'github.com':['gist.github.com','XX.github.com'],
	 'stackoverflow.com':['XX.stackoverflow.com',]} 

	Task Format:
		Task:
		target|dict|dict_path|start_line|scan_lines
		target|comp|charset|begin_str|end_str
		target;target;target|crawl
		Result:
		URL;URL;URL
		no dir
	Example:
		Put task:
		github.com|dict|./dictionary/dir.dict|1000|900
		github.com|comp|ABCabc|A|cccc
		Get result:
		no dir
		https://github.com/something;https://github.com/something/something
		https://github.com/something,GET,id,number,class;https://github.com/something/something,POST,XX,XX
	"""
	def __init__(self, args):
		super(Master, self).__init__()
		self._args = args	

		if self._args.dir_http_port=='' and self._args.dir_https_port=='':
			raise SwarmUseException('at least one http or https port should be specified')
		
		http_portl=[]
		https_portl=[]
		# just used for check validity here
		try:
			if self._args.dir_http_port!='':
				http_portl=parse_port_list(self._args.dir_http_port)
			if self._args.dir_https_port!='':
				https_portl=parse_port_list(self._args.dir_https_port)
		except SwarmParseException as e:
			raise SwarmUseException('invalid http or https port argument in directory scan')

		# initial _url_list_orig.
		# it should prepare a list contains valid targets like:
		# 
		# ['http://github.com:81','http://XX.com:80','https://github.com:9090']
		self._url_list_orig=[]
		for curhost in self._args.target_list:
			for curport in http_portl:
					self._url_list_orig.append('http://'+curhost+':'+str(curport))
			for curport in https_portl:
					self._url_list_orig.append('https://'+curhost+':'+str(curport))

		if self._args.dir_maxdepth<0:
			raise SwarmUseException('directory max depth can not be negative')
		if self._args.dir_maxdepth==0:
			self._args.dir_maxdepth=9999
		
		# initial url_list 
		self._url_list=[x+'/' for x in self._url_list_orig]	
		# record current dir depth
		self._curdepth=0

	def generate_subtasks(self):
		"""
		Decomposition directory and file scan task and distribute tasks, get result from swarm.
		Task granularity should not be too small or too huge.
		"""
		self._curdepth+=1
		# if it is out of range, end this task
		if self._curdepth>self._args.dir_maxdepth:
			return []
		# if there is no dir can be scan, end this task
		if len(self._url_list)==0:
			return []
		# begin discomposition
		if self._args.dir_compbrute==True:
			try:
				# generate list of subtasks 
				subtasklist=generate_compbrute_subtask(self._url_list,self._args.dir_len,
					self._args.dir_charset,self._args.task_granularity)
			except SwarmParseException as e:
				raise SwarmUseException('invalid directory '+str(e)+', or format error')
		else:
			if dict=='':
				raise SwarmUseException('directory dictionary need to be provided')
			try:
				# generate list of subtasks
				subtasklist=generate_dictbrute_subtask(self._url_list,self._args.dir_dict,
					self._args.task_granularity)
			except IOError as e:
				raise SwarmUseException('can not open dictionary for directory scan, path:%s'%(dict))
		# clear url_list for next iteration
		self._url_list=[]
		return subtasklist

	def handle_result(self,result):
		if result!='no dir or file':
			result_list=result.split(';')
			# store result into url_list for next scan 
			for x in result_list:
				if x[-1]=='/':
					self._url_list.append(x)
			# store result into final result
			key='/'.join(result_list[0].split('/')[:3])
			self._args.coll.insert({'domain':key,'content':[x[len(key):] for x in result_list]})


	def report(self):
		for curdomain in self._url_list_orig:
			all_content=[]
			content=self._args.coll.find({'domain':curdomain})
			for cur in content:
				all_content.extend(cur['content'])
			print '============= scan result of '+curdomain+' =============='
			print '\n'.join(all_content)
		print '================================================================='		

class Slave(object):
	"""
	Directory and file scanner providing functions of crawler, complete brute force and 
	dictionary brute force.

	Task Format:
		Task:
		target|dict|dict_path|start_line|scan_lines
		target|comp|charset|begin_str|end_str
		target;target;target|crawl
		Result:
		URL;URL;URL
		no dir
	Example:
		Put task:
		github.com|dict|./dictionary/dir.dict|1000|900
		github.com|comp|ABCabc|A|cccc
		Get result:
		no dir
		https://github.com/something;https://github.com/something/something
		https://github.com/something,GET,id,number,class;https://github.com/something/something,POST,XX,XX

	"""
	def __init__(self, args):
		super(Slave, self).__init__()
		self._pool=Pool(args.thread_num)
		self._timeout=args.dir_timeout
		self._not_exist_flag=args.dir_not_exist
		self._quick_mode=args.dir_quick_scan

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
			cur_target=target+cur
			resultl.append(self._pool.apply_async(self._scan_target,args=(cur_target,)))
		return self._get_result(resultl)

	def dict_brute(self,target,dict_path,start_line,lines):
		resultl=[]
		lines=int(lines,10)
		start_line=int(start_line,10)
		with open(dict_path) as fp:
			fcontent=fp.readlines()
			for cur_index in range(lines):
				cur_target=target+fcontent[start_line+cur_index-1].strip()
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
			result='no dir or file'
		else:
			result=result[:-1]
		return result

	def _scan_target(self,target):
		LOG.debug('scan target: %s'%target)
		if self._quick_mode:
			return self._scan_target_quick(target)
		else:
			return self._scan_target_normal(target)

	def _scan_target_normal(self,target):
		try:
			r=requests.head(target)
			#it maybe a directory
			if self._check_eponymous_dir(r,target):
				return target+'/;'

			if self._check_exist_code(r.status_code):
				# check content
				r=requests.get(target)
				if self._check_exist_code(r.status_code):
					for cur in self._not_exist_flag:
						if r.content.find(cur)!=-1:
							return ''
					return target+';'
			return ''
		except Exception as e:
			return ''

	def _scan_target_quick(self,target):
		try:
			r=requests.head(target)
			#it maybe a directory
			if self._check_eponymous_dir(r,target):
				return target+'/;'

			if self._check_exist_code(r.status_code):
				return target+';'
			else:
				return ''
		except Exception as e:
			return ''

	def _check_exist_code(self,code):
		if code<300 or code==401 or code==403:
			return True
		return False

	def _check_eponymous_dir(self,r,target):
		"""
		Args:
			r: response of request to URL 'target'
			target: URL of one file which wait to be check wether exist eponymous directory
		Returns:
			True if the response means there is a eponymous directory with target file.
			Otherwise return False.
		"""
		if r.status_code==301:
			if r.headers['Location']==target+'/':
				return True
			else:
				targetl=target.split('/')
				targetl[2]=targetl[2].split(':')[0]
				target='/'.join(targetl)
				if r.headers['Location']==target+'/':
					return True
		return False
		
