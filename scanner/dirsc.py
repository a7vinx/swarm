#!/user/bin/python
# -*- coding: utf-8 -*-

import requests
from multiprocessing.dummy import Pool
from multiprocessing import TimeoutError

from lib.core.logger import LOG
from lib.utils.bfutils import generate_bflist

class DirScanner(object):
	"""
	Directory and file scanner providing functions of crawler, complete brute force and 
	dictionary brute force.
	"""
	def __init__(self,thread_num,timeout,not_exist_flag,quick_mode=False):
		super(DirScanner, self).__init__()
		self._pool=Pool(thread_num)
		self._timeout=timeout
		self._not_exist_flag=not_exist_flag
		self._quick_mode=quick_mode
		
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

	def crawl(self):
		pass

	def _get_result(self,resultl):
		result=''
		# get result from list
		for cur in resultl:
			try:
				result+=cur.get(timeout=self._timeout)
			except TimeoutError, e:
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
		except Exception, e:
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
		except Exception, e:
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

