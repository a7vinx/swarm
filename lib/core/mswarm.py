#!/user/bin/python
# -*- coding: utf-8 -*-

import socket
import time
import multiprocessing
from threading import Thread
from lib.core.swarm_manager import SwarmManager
from lib.parse.host import getlist
from lib.parse.host import getswarmlist
from lib.parse.host import removeip
from lib.parse.host import getiplist
from lib.core.logger import LOG


class MSwarm(object):
	"""docstring for MSwarm"""
	def __init__(self, args):
		self._args=args
		self._target_list=getlist(**{'target':args.target,'target_file':args.target_file})
		
		if args.waken_cmd!='':
			self._swarm_list,self._swarm_port_list=getswarmlist(**{'swarm':args.swarm,'swarm_file':args.swarm_file})
		else:
			self._swarm_list=getlist(**{'target':args.swarm,'target_file':args.swarm_file})

	def waken_swarm(self):
		"""
		waken all slave hosts to run swarm-s.py and send args to them
		"""
		if self._args.waken_cmd!='':
			LOG.info('sending waken command "%s"to swarm...'%(self._args.waken_cmd.replace('PORT','-p %d'%self._args.s_port)))
			self._send2slave(self._args.waken_cmd.replace('PORT','-p %d'%self._args.s_port))
		# time for slave host to create listen on target port
		time.sleep(1)
		s_args=self._parse_args_for_swarm()
	
		if self._args.sync_data==True:
			s_args+='__SYNC__'
		else:
			s_args+='__CEND__'
		r=self._send2swarm_r(s_args)
		LOG.info('waken %d slaves in swarm'%(len(r)))
		
		# do data sync here
		if self._args.sync_data==True:	
			LOG.info('begin to synchronize data...')
			self._sync_data()
			LOG.info('data synchronize completed')

	def parse_distribute_task(self):
		self._manager=SwarmManager(address=('', self._args.m_port), 
			authkey=self._args.authkey)
		self._manager.start()
		self._task_queue = self._manager.get_task_queue()
		self._result_queue = self._manager.get_result_queue()
		LOG.info('begin to parse task...')


		if self._args.enable_domain_scan==True:
			self.scan_domain()


		for i in range(0,20):
			self._task_queue.put('request')
			LOG.debug(self._result_queue.get())

	def scan_domain(self):
		"""
		"""


		# if self._args.domain_compbrute==True:

		# else:
		# 	try:
		# 		# get total number of dictionary lines
		# 		with open(self._args.domain_dict) as fp:
		# 			sumline=sum(1 for i in fp)

		# 		cur_index=0
		# 		while True:
		# 			task='__doms__'
		# 			task+=
		# 		self._task_queue.put()

		# 	except IOError, e:
		# 		LOG.error('can not open dictionary for domain scan, path:%s'%(self._args.domain_dict))
		# 		raise
			

	def scan_dir():
		pass

	def scan_web_vul():
		pass

	def scan_host_vul():
		pass

	def try_exp():
		pass

	def try_post_exp():
		pass

	def _parse_args_for_swarm(self):
		s=''
		s=self._put_key_value(s,'m_addr',self._args.m_addr)
		s=self._put_key_value(s,'m_port',self._args.m_port)
		s=self._put_key_value(s,'authkey',self._args.authkey)
		# cut off the last ','
		s=s[:-1]
		LOG.debug('args pass to swarm-s: '+s)
		return s

	def _put_key_value(self,s,key,value):
		s+=key
		s+=':'
		s+=str(value)
		s+=','
		return s

	def _sync_data(self):
		self._send2swarm_r('sync')
		self._send2swarm_r('sync')
		# TODO: do data sync here
		pass

	def _send2swarm_r(self,content):
		ret=[]
		for index in range(0,len(self._swarm_list)):
			LOG.info('starting thread %d to deal socket'%(index))
			t=Thread(target=self._send2one_r,
				args=(content,self._swarm_list[index],self._args.s_port,ret))
			t.start()
			t.join()
		return ret


	def _send2slave(self,content):
		for index in range(0,len(self._swarm_list)):
			LOG.info('starting thread %d to deal socket'%(index))
			t=Thread(target=self._send2one,
				args=(content,self._swarm_list[index],self._swarm_port_list[index]))
			t.start()
			t.join()

	def _send2one(self,content,ip,port):
		try:
			s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			s.settimeout(self._args.timeout)
			LOG.info('connecting to %s:%d...'%(ip,port))
			s.connect((ip,port))
			s.send(content)
			s.close()
			LOG.info('connection to %s:%d close'%(ip,port))
		except socket.timeout,e:
			LOG.warning('%s:%d lost response'%(ip,port))
		except socket.error,arg:
			LOG.warning('socket error while connecting to %s:%d errno %d: %s'%(ip,port,arg[0],arg[1]))

	def _send2one_r(self,content,ip,port,result):
		try:
			s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			s.settimeout(self._args.timeout)
			LOG.info('connecting to %s:%d...'%(ip,port))
			s.connect((ip,port))
			s.send(content.replace('__EOF__','__EOF___'))
			s.send('__EOF__')
			r=s.recv(4096)
			if r!='':
				result.append(r)
			# LOG.debug('receive from %s:%d: %s'%(ip,port,buff))
			s.close()
			LOG.debug('connection to %s:%d close'%(ip,port))
		except socket.timeout,e:
			LOG.warning('%s:%d lost response'%(ip,port))
			return ''
		except socket.error,arg:
			LOG.warning('socket error while connecting to %s:%d errno %d: %s'%(ip,port,arg[0],arg[1]))
			return ''

