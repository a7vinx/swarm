#!/user/bin/python
# -*- coding: utf-8 -*-

import socket
from multiprocessing.dummy import Pool
from multiprocessing import TimeoutError

from lib.utils.bfutils import generate_bflist
from lib.core.logger import LOG

class DomainScanner(object):
	"""
	Subdomain name scanner provides functions complete brute force and dictionary 
	brute force.
	"""
	def __init__(self,thread_num,timeout):
		super(DomainScanner, self).__init__()
		self._pool=Pool(thread_num)
		self._timeout=timeout
	
	def complete_brute(self,target,charset,begin_str,end_str):
		result=''
		resultl=[]
		bflist=generate_bflist(charset,begin_str,end_str)
		for cur in bflist:
			cur_target=cur+'.'+target
			resultl.append(self._pool.apply_async(self._scan_target,args=(cur_target,)))
		# get result from list
		for cur in resultl:
			try:
				result+=cur.get(timeout=self._timeout)
			except TimeoutError, e:
				continue
		# deal with result
		if result=='':
			result='no subdomain'
		else:
			result=result[:-1]
		return result

	def dict_brute(self,target,dict_path,start_line,lines):
		result=''
		resultl=[]
		lines=int(lines,10)
		start_line=int(start_line,10)
		with open(dict_path) as fp:
			fcontent=fp.readlines()
			for cur_index in range(lines):
				cur_target=fcontent[start_line+cur_index-1].strip()+'.'+target
				resultl.append(self._pool.apply_async(self._scan_target,args=(cur_target,)))
			# get result from list
			for cur in resultl:
				try:
					result+=cur.get(timeout=self._timeout)
				except TimeoutError, e:
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
		except Exception, e:
			return ''

	