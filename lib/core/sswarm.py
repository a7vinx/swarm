#!/user/bin/python
# -*- coding: utf-8 -*-

import socket
import time
import multiprocessing
from lib.core.swarm_manager import SwarmManager
from lib.core.logger import LOG

class SSwarm(object):
	"""docstring for SSwarm"""
	def __init__(self,s_port):
		super(SSwarm, self).__init__()
		self._s_port=s_port
		self._args={}

	def get_parse_args(self):
		# first receive args
		args=self._receive_master()
		sync_flag=args[-8:]
		args=args[:-8]
		self._parse_args(args)
		LOG.debug('complete parsing args')

		if sync_flag=='__SYNC__':
			# do data sync here
			LOG.debug('begin to synchronize data...')
			self._sync_data()
			LOG.debug('data synchronize completed')

	def get_do_task(self):
		self._manager=SwarmManager(address=(self._args['m_addr'], self._args['m_port']),
				authkey=self._args['authkey'])
		self._manager.connect()

		self._task_queue = self._manager.get_task_queue()
		self._result_queue = self._manager.get_result_queue()
		LOG.debug('begin to get and do task...')

		for i in range(0,10):
			LOG.debug(self._task_queue.get())
			self._result_queue.put('ack')
		# ready
		# while True:
		# 	pass

	def _parse_args(self,args):
		l=args.split(',')
		for cur in l:
			pair=cur.split(':')
			LOG.debug('key: %s, value: %s'%(pair[0],pair[1]))
			self._args[pair[0]]=pair[1]
		self._unite_args()

	def _unite_args(self):
		self._args['m_port']=int(self._args['m_port'],10)

	def _sync_data(self):
		print self._receive_master()
		print self._receive_master()
		# TODO: do data sync here
		pass
		
	def _do_domain_scan():
		pass

	def _do_dir_scan():
		pass

	def _do_web_vul_scan():
		pass

	def _do_host_vul_scan():
		pass

	def _do_try_exp():
		pass

	def _do_try_post_exp():
		pass

	def _receive_master(self):
		s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		# incase 'Address already in use error'
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind(('',self._s_port))
		LOG.debug('listen on port:%d'%self._s_port)
		s.listen(1)
		sock, addr=s.accept()
		LOG.debug('receive from master host...')
		buff=''
		while True:
			d=sock.recv(4096)
			buff+=d
			if d.find('__EOF__')!=-1:
				break
		sock.send('ack')
		sock.close()
		s.close()
		# cut off last __EOF__
		buff=buff[:-7]
		# return to origin args
		buff=buff.replace('__EOF___','__EOF__')
		return buff



