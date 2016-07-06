#!/user/bin/python
# -*- coding: utf-8 -*-

import socket
import time
import multiprocessing
import threading 
from lib.core.swarm_manager import MSwarmManager
from lib.parse.host import getlist
from lib.parse.host import getswarmlist
from lib.parse.host import removeip
from lib.parse.host import getiplist
from lib.core.logger import LOG
from lib.core.exception import SwarmUseException
from lib.utils.bfutils import generate_bflist


class MSwarm(object):
	"""
	A role of master in the distributed system.
	"""
	def __init__(self, args):
		self._args=args
		self._target_list=getlist(args.target,args.target_file)
		
		if args.waken_cmd!='':
			self._swarm_list,self._swarm_port_list=getswarmlist(args.swarm,args.swarm_file)
		else:
			self._swarm_list=getlist(args.swarm,args.swarm_file)

	def waken_swarm(self):
		"""
		Waken all slave hosts to run swarm-s.py and send args to them.
		Synchronize data if need.
		"""
		if self._args.waken_cmd!='':
			LOG.info('sending waken command "%s"to swarm...'%(self._args.waken_cmd.replace('ARGS','-p %d'%self._args.s_port)))
			self._send2slave(self._args.waken_cmd.replace('ARGS','-p %d'%self._args.s_port))
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
		self._manager=MSwarmManager(self._args.timeout,address=('', self._args.m_port), 
			authkey=self._args.authkey)
		LOG.info('begin to parse task...')

		if self._args.enable_domain_scan==True:
			self.scan_domain()


		self._shutdown()

	def scan_domain(self):
		"""
		Decomposition domain name scan task and distribute tasks, get result from swarm.
		Task granularity should not be too small or too huge.
		Task format:
		__doms__:task_index:domain name:dict:dict_path:start_line:scan_lines
		__doms__:task_index:domain name:comp:charset:begin_str:end_str
		Result format:
		__doms__:task_index:result
		Example:
		put task:
		__doms__:26:github.com:dict:2000:3000
		__doms__:980:github.com:comp:ABCDEFGHIJKLMN8980:DAAA:D000
		get result:
		__doms__:980:gist.github.com;XX.github.com
		__doms__:980:no subdomain
		"""	
		scan_result=[]
		domain_list=removeip(self._target_list)
		if len(domain_list)==0:
			LOG.critical('domain name must be provided')
			raise SwarmUseException('domain name must be provided')			

		if self._args.domain_maxlevel<=0:
			LOG.critical('subdomain name max level must be positive')
			raise SwarmUseException('subdomain name max level must be positive')

		# begin to discomposition 
		for curlevel in range(self._args.domain_maxlevel):	
			self._manager.init_task_statistics()
			if self._args.domain_compbrute==True:
				# parse interval of subdomain name length
				try:
					midindex=self._args.domain_levellen.find('-')
					minlen=int(self._args.domain_levellen[:midindex],10)
					maxlen=int(self._args.domain_levellen[midindex+1:],10)
				except Exception, e:
					LOG.critical('invalid subdomain name length interval, or format error')
					raise SwarmUseException('invalid subdomain name length interval, or format error')
				# parse char set
				charset=self._parse_charset()
				task_granularity=4
				for cur_target in domain_list:
					begin_str=''
					if maxlen<task_granularity:
						begin_str=minlen*charset[0]
						end_str=maxlen*charset[-1]
						task=':'.join([cur_target,'comp',charset,begin_str,end_str])
						self._manager.put_task('__doms__',task)
						continue

					if minlen<task_granularity:
						begin_str=minlen*charset[0]
						end_str=(task_granularity-1)*charset[-1]
						task=':'.join([cur_target,'comp',charset,begin_str,end_str])
						self._manager.put_task('__doms__',task)

					bflist=generate_bflist(charset,charset[0],(maxlen-task_granularity+1)*charset[-1])
					for pre_str in bflist:
						begin_str=pre_str+(task_granularity-1)*charset[0]
						end_str=pre_str+(task_granularity-1)*charset[-1]
						task=':'.join([cur_target,'comp',charset,begin_str,end_str])
						self._manager.put_task('__doms__',task)
			# use dictionary 
			else:
				if self._args.domain_dict=='':
					LOG.critical('domain name dictionary need to be provided')
					raise SwarmUseException('domain name dictionary need to be provided')

				try:
					# get total number of dictionary lines
					with open(self._args.domain_dict) as fp:
						sumline=sum(1 for i in fp)
				except IOError, e:
					LOG.critical('can not open dictionary for domain scan, path:%s'%(self._args.domain_dict))
					raise SwarmUseException('can not open dictionary for domain scan, path:%s'%(self._args.domain_dict))

				task_granularity=1000
				for cur_target in domain_list:
					# begin from fisrt line
					cur_line=1
					while True:
						# after next calculation, cur_line point to next start line 
						if (cur_line+task_granularity)>sumline:
							lines=sumline-cur_line+1
						else:
							lines=task_granularity
						task=':'.join([cur_target,'dict',self._args.domain_dict,str(cur_line),str(lines)])
						self._manager.put_task('__doms__',task)
						# update current line 
						cur_line+=task_granularity
						if cur_line>sumline:
							break
			# get scan result
			domain_list=[]
			self._manager.prepare_get_result()
			while True:
				result=self._manager.get_result()
				if result=='':
					break
				if result!='no subdomain':
					domain_list.extend(result.split(';'))
				# update result list
			scan_result.extend(domain_list)
		# do report
		LOG.info('scan result:%s'%scan_result)
		return scan_result
	
	def scan_dir():
		"""
		"""
		pass

	def scan_web_vul():
		pass

	def scan_host_vul():
		pass

	def try_exp():
		pass

	def try_post_exp():
		pass

	def _shutdown(self):
		if self._args.process_num==0:
			# ensure all process can be notified
			off_num=16
		else:
			off_num=self._args.process_num
		for cur in range(len(self._swarm_list)*off_num):
			self._manager.put_task('__off__:','')
		time.sleep(3)
		self._manager.shutdown()

	def _parse_charset(self):
		try:
			charset=self._args.domain_charset
			while True:
				index=charset.find('-')
				if index==-1:
					break
				begin_chr=charset[index-1]
				end_chr=charset[index+1]
				dst=''
				for x in range(ord(begin_chr),ord(end_chr)+1):
					dst+=chr(x)
				charset=charset.replace(begin_chr+'-'+end_chr,dst)
			ret = ''.join(x for i, x in enumerate(charset) if charset.index(x) == i) 
			LOG.debug('charset: %s'%ret)
			return ret
		except Exception, e:
			LOG.critical('invalid subdomain name charset, or format error')
			# raise SwarmUseException('invalid subdomain name charset, or format error')
			raise

	def _parse_args_for_swarm(self):
		s=''
		s=self._put_key_value(s,'m_addr',self._args.m_addr)
		s=self._put_key_value(s,'m_port',self._args.m_port)
		s=self._put_key_value(s,'authkey',self._args.authkey)
		s=self._put_key_value(s,'process_num',self._args.process_num)
		s=self._put_key_value(s,'thread_num',self._args.thread_num)
		s=self._put_key_value(s,'domain_timeout',self._args.domain_timeout)
		# remove the last ','
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
			t=threading.Thread(target=self._send2one_r,
				args=(content,self._swarm_list[index],self._args.s_port,ret))
			t.start()
			t.join()
		return ret


	def _send2slave(self,content):
		for index in range(0,len(self._swarm_list)):
			LOG.info('starting thread %d to deal socket'%(index))
			t=threading.Thread(target=self._send2one,
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
			LOG.error('socket error while connecting to %s:%d errno %d: %s'%(ip,port,arg[0],arg[1]))

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
			s.close()
			LOG.debug('connection to %s:%d close'%(ip,port))
		except socket.timeout,e:
			LOG.warning('%s:%d lost response'%(ip,port))
			return ''
		except socket.error,arg:
			LOG.error('socket error while connecting to %s:%d errno %d: %s'%(ip,port,arg[0],arg[1]))
			return ''

