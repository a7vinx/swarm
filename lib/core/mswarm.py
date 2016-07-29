#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import time
import multiprocessing
import threading 
import importlib
import json
import Queue
from lib.core.manager import MSwarmManager
from lib.parse.host import getlist
from lib.parse.host import getswarmlist
from lib.parse.host import removeip
from lib.parse.host import getiplist
from lib.core.logger import LOG
from lib.core.logger import REPORT
from lib.core.database import init_db
from lib.core.exception import SwarmBaseException
from lib.core.exception import SwarmUseException
from lib.core.exception import SwarmFileException
from lib.core.exception import SwarmNetException
from lib.core.exception import SwarmParseException
from lib.core.exception import SwarmModuleException
from lib.core.exception import SwarmSlaveException


class MSwarm(object):
	"""
	A role of master in the distributed system.
	"""
	def __init__(self, args):
		self._args=args
		self._swarm_num=0
		try:
			LOG.info('begin to parse target list')
			# parse target list
			self._args.target_list=getlist(args.target,args.target_file)
			LOG.log(REPORT,'target list parse completed')
		except SwarmBaseException as e:
			raise SwarmUseException('parse target error: '+str(e))

		try:	
			LOG.info('begin to parse swarm list')
			# parse swarm list
			if args.waken_cmd!='':
				self._swarm_list,self._swarm_port_list=getswarmlist(args.swarm,args.swarm_file)
			else:
				self._swarm_list=getlist(args.swarm,args.swarm_file)
			LOG.log(REPORT,'swarm list parse completed')
		except SwarmBaseException as e:
			raise SwarmUseException('parse swarm error: '+str(e))

	def waken_swarm(self):
		"""
		Waken all slave hosts to run swarm-s and send args to them.
		Synchronize data if need.
		"""
		if self._args.waken_cmd!='':
			LOG.info('send waken command "%s"to swarm'%(self._args.waken_cmd.replace('ARGS',
				'-p %d'%self._args.s_port)))
			self._send2slave(self._args.waken_cmd.replace('ARGS','-p %d'%self._args.s_port))
			LOG.log(REPORT,'sending waken command completed')
			LOG.info('try to detect swarm status')
		# time for slave host to create listen on target port
		time.sleep(2)
		s_args=self._parse_args_for_swarm()
	
		if self._args.sync_data==True:
			s_args+='__SYNC__'
		else:
			s_args+='__CEND__'
		r=self._send2swarm_r(s_args)
		self._swarm_num=len(r)
		LOG.log(REPORT,'waken %d slaves in swarm'%self._swarm_num)
		
		# do data sync here
		if self._args.sync_data==True:	
			LOG.info('begin to synchronize data...')
			self._sync_data()
			LOG.info('data synchronize completed')

	def parse_distribute_task(self):
		# do some common check here
		if self._args.task_granularity<0 or self._args.task_granularity>3:
			raise SwarmUseException('invalid task granularity, it should be one number of 1-3')
		if self._args.process_num<0:
			raise SwarmUseException('process number can not be negative')
		if self._args.thread_num<=0:
			raise SwarmUseException('thread number should be positive')

		# connect to db server
		LOG.info('try to connect to db server: %s:%d'%(self._args.db_addr,self._args.db_port))
		self._args.db,self._args.coll=init_db(self._args.db_addr,self._args.db_port,self._args.mod)
		LOG.info('Connection to db server completed')
		# start the manager
		self._manager=MSwarmManager(self._args.timeout,address=('', self._args.m_port), 
			authkey=self._args.authkey)
		try:
			module=importlib.import_module('modules.'+self._args.mod+'.'+self._args.mod)
		except ImportError as e:
			raise SwarmModuleException('an error occured when load module:'+self._args.mod)	
		LOG.info('load module: '+self._args.mod)
		LOG.info('begin to decompose task...')
		mod_master=getattr(module,'Master')(self._args)

		# begin first round of tasks decomposition and distribution
		roundn=0
		self._manager.init_task_statistics()
		while True:
			subtaskl=mod_master.generate_subtasks()
			taskn=len(subtaskl)
			if taskn==0:
				break
			roundn+=1
			LOG.log(REPORT,'begin round %d'%roundn)
			LOG.info('round %d: put task into queue...'%roundn)
			for cur in subtaskl:
				self._manager.put_task(self._args.mod,cur)
			LOG.log(REPORT,'round %d: %d tasks have been put into queue'%(roundn,taskn))
			LOG.info('round %d: get result from swarm...'%roundn)

			# get result
			confirmedn=0
			self._manager.prepare_get_result()
			while True:
				try:
					result=self._manager.get_result()
					if result=='':
						break
					confirmedn+=1
					LOG.log(REPORT,'round %d: %d/%d tasks have been completed'%(roundn,
						confirmedn,taskn))
					mod_master.handle_result(result)
				except Queue.Empty as e:
					# check number of slave host, if someone has lost response, reorganize tasks 
					# in queue.
					LOG.info('try to detect swarm status')
					r=self._send2swarm_r('ack')
					if len(r)<self._swarm_num:
						LOG.warning('%d of swarm has lost response. now total swarm:%d'
							%(self._swarm_num-len(r),len(r)))
						self._swarm_num=len(r)
						# if no swarm left
						if self._swarm_num==0:
							raise SwarmSlaveException('no swarm left. task failed')
						LOG.log(REPORT,'reorganize tasks in queue...')
						self._manager.reorganize_tasks()
						LOG.log(REPORT,'reorganization completed')
					else:
						LOG.log(REPORT,'all swarm works fine. now num: %d'%self._swarm_num)
					# continue 
			LOG.log(REPORT,'round %d over'%roundn)
		LOG.log(REPORT,'all tasks have been comfirmed')
		# do final report now
		mod_master.report()
		self._shutdown()

	def _shutdown(self):
		if self._args.process_num==0:
			# ensure all process can be notified
			off_num=16
		else:
			off_num=self._args.process_num
		for cur in range(len(self._swarm_list)*off_num):
			self._manager.put_task('__off__','|')
		time.sleep(2)
		self._manager.shutdown()
		# drop collection 
		self._args.db.drop_collection(self._args.coll)

	def _sync_data(self):
		self._send2swarm_r('sync')
		self._send2swarm_r('sync')
		# TODO: do data sync here
		pass

	def _parse_args_for_swarm(self):
		return json.dumps(vars(self._args))

	def _send2swarm_r(self,content):
		LOG.info('connect to swarm...')
		ret=[]
		for index in range(0,len(self._swarm_list)):
			t=threading.Thread(target=self._send2one_r,
				args=(content,self._swarm_list[index],self._args.s_port,ret))
			t.start()
			t.join()
		LOG.info('get %d response from swarm'%len(ret))
		return ret


	def _send2slave(self,content):
		for index in range(0,len(self._swarm_list)):
			t=threading.Thread(target=self._send2one,
				args=(content,self._swarm_list[index],self._swarm_port_list[index]))
			t.start()
			t.join()

	def _send2one(self,content,ip,port):
		try:
			s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			s.settimeout(self._args.timeout)
			LOG.debug('connect to %s:%d...'%(ip,port))
			s.connect((ip,port))
			s.send(content)
			s.close()
			LOG.debug('connection to %s:%d close'%(ip,port))
		except socket.timeout as e:
			LOG.warning('%s:%d lost response'%(ip,port))
		except socket.error as arg:
			LOG.error('socket error while connecting to %s:%d errno %d: %s'%(ip,port,arg[0],arg[1]))

	def _send2one_r(self,content,ip,port,result):
		try:
			s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			s.settimeout(self._args.timeout)
			LOG.debug('connect to %s:%d...'%(ip,port))
			s.connect((ip,port))
			s.send(content.replace('__EOF__','__EOF___'))
			s.send('__EOF__')
			r=s.recv(4096)
			if r!='':
				result.append(r)
			s.close()
			LOG.debug('connection to %s:%d close'%(ip,port))
		except socket.timeout as e:
			LOG.warning('%s:%d lost response'%(ip,port))
			return ''
		except socket.error as arg:
			LOG.error('socket error while connecting to %s:%d errno %d: %s'%(ip,port,arg[0],arg[1]))
			return ''

