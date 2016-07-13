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
from lib.core.exception import SwarmParseException
from lib.utils.bfutils import generate_bflist
from lib.utils.sitemap import draw_sitemap


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
		time.sleep(2)
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
		# scan subdomain name
		if self._args.enable_domain_scan==True:
			result=self.scan_domain(targetl=self._target_list,maxlevel=self._args.domain_maxlevel,
				compbrute=self._args.domain_compbrute,dict=self._args.domain_dict,
				charset=self._args.domain_charset,levellen=self._args.domain_levellen)
		# scan directory and file
		if self._args.enable_dir_scan==True:
			result=self.scan_dir(targetl=self._target_list,enable_crawler=self._args.dir_enable_crawler,
				crawl_seed=self._args.dir_crawl_seed,http_port=self._args.dir_http_port,
				https_port=self._args.dir_https_port,enable_brute=self._args.dir_enable_brute,
				maxdepth=self._args.dir_max_depth,compbrute=self._args.dir_compbrute,
				dict=self._args.dir_dict,charset=self._args.dir_charset,dirlen=self._args.dir_len)
			draw_sitemap(result)
		# scan web vulnerabilities
		if self._args.enable_web_vul_scan==True:
			pass

		self._shutdown()

	def scan_domain(self,targetl,maxlevel,compbrute,dict,charset,levellen):
		"""
		Decomposition domain name scan task and distribute tasks, get result from swarm.
		Task granularity should not be too small or too huge.

		Format:
			Task format:
			__doms__|task_index|domain name|dict|dict_path|start_line|scan_lines
			__doms__|task_index|domain name|comp|charset|begin_str|end_str
			Result format:
			__doms__|task_index|result
		Example:
			put task:
			__doms__|26|github.com|dict|./dictionary/domain.dict|2000|3000
			__doms__|980|github.com|comp|ABCDEFGHIJKLMN8980|DAAA|D000
			get result:
			__doms__|980|gist.github.com;XX.github.com
			__doms__|980|no subdomain

		Returns:
			A dict using domain name as keys and a list contains subdomain names as values.
			For example:

			{'github.com':['gist.github.com','XX.github.com'],
			 'stackoverflow.com':['XX.stackoverflow.com',]} 

		"""	
		scan_result={}
		domain_list=removeip(targetl)
		# initial scan result dict
		for x in domain_list:
			scan_result[x]=[]

		if len(domain_list)==0:
			LOG.critical('domain name must be provided')
			raise SwarmUseException('domain name must be provided')			

		if maxlevel<=0:
			LOG.critical('subdomain name max level must be positive')
			raise SwarmUseException('subdomain name max level must be positive')

		# begin to discomposition 
		for curlevel in range(maxlevel):	
			self._manager.init_task_statistics()
			if compbrute==True:				
				try:
					task_granularity=4
					# generate list of subtasks
					subtasklist=self._generate_compbrute_subtask(domain_list,levellen,charset,
						task_granularity)
					for cursubtask in subtasklist:
						self._manager.put_task('__doms__',cursubtask)
				except SwarmParseException, e:
					LOG.critical('invalid subdomain name '+str(e)+', or format error')
					raise SwarmUseException('invalid subdomain name '+str(e)+', or format error')
			# use dictionary 
			else:
				if dict=='':
					LOG.critical('domain name dictionary need to be provided')
					raise SwarmUseException('domain name dictionary need to be provided')

				try:
					task_granularity=1000
					# generate list of subtasks
					subtasklist=self._generate_dictbrute_subtask(domain_list,dict,task_granularity)
					for cursubtask in subtasklist:
						self._manager.put_task('__doms__',cursubtask)
				except IOError, e:
					LOG.critical('can not open dictionary for domain scan, path:%s'%(dict))
					raise SwarmUseException('can not open dictionary for domain scan, path:%s'%(dict))	
			# get scan result
			domain_list=[]
			self._manager.prepare_get_result()
			while True:
				result=self._manager.get_result()
				if result=='':
					break
				if result!='no subdomain':
					resultl=result.split(';')
					# update domain name list for next iteration
					domain_list.extend(resultl)
					# add it into scan result meanwhile
					for curkey in scan_result:
						if resultl[0].find(curkey)==len(resultl[0])-len(curkey):
							scan_result[curkey].extend(resultl)
							break
			# finish loop
		# finish loop 
		# do report
		LOG.info('scan result:%s'%scan_result)
		return scan_result

	def scan_dir(self,targetl,enable_crawler,crawl_seed,http_port,https_port,enable_brute,maxdepth,
		compbrute,dict,charset,dirlen):
		"""
		Decomposition directory and file scan task and distribute tasks, get result from swarm.
		Task granularity should not be too small or too huge.
		If option dir_crawler is set, do crawling first.

		Format:
			Task format:
			__dirs__|task_index|target|dict|dict_path|start_line|scan_lines
			__dirs__|task_index|target|comp|charset|begin_str|end_str
			__dirs__|task_index|target;target;target|crawl
			Result format:
			__dirs__:task_index:result
		Example:
			Put task:
			__dirs__|90|github.com|dict|./dictionary/dir.dict|1000|900
			__dirs__|91|github.com|comp|ABCabc|A|cccc
			Get result:
			__dirs__|90|no dir
			__dirs__|1|github.com/something;github.com/something/something
			__dirs__|4|github.com/something,GET,id,number,class;github.com/something/something,POST,XX,XX

		Returns:
			A dict using protocal+ip/domain name+port as keys and a list contains directory 
			infomation as values. For example:

			{'http://github.com:80':['/','stars','XX/'],
			 'https://github.com:443':['/','XX'],
			 'http://stackoverflow.com:80':['/','XX']}
		"""

		if http_port=='' and https_port=='':
			LOG.critical('at least one http or https port should be specified')
			raise SwarmUseException('at least one http or https port should be specified')
		
		# just used for check validity here
		try:
			if http_port!='':
				http_portl=self._parse_port_list(http_port)
			if https_port!='':
				https_portl=self._parse_port_list(https_port)
		except SwarmParseException, e:
			LOG.critical('invalid http or https port argument in directory scan')
			raise SwarmUseException('invalid http or https port argument in directory scan')

		# TODO:
		# First check service running on target host to make sure there is web server running on 
		# target port. Then initial scan_result use port scan result.
		# It should prepare a dict contains valid targets like:
		# 
		# {'http://github.com:80':['/',],
		#  'https://github.com:443':['/',]}
		port_result=self.scan_host(targetl=targetl,enable_port_scan=True,
			ports=(http_port+'|'+https_port).strip('|'))

		scan_result={}
		for curhost in port_result:
			for curport,portstatus in port_result[curhost].iteritems():
				if portstatus[1] in ['http','https']:
					scan_result[portstatus[1]+'://'+curhost+':'+str(curport)]=['/',]

		if enable_brute:
			if maxdepth<0:
				LOG.critical('directory max depth can not be negative')
				raise SwarmUseException('directory max depth can not be negative')
			if maxdepth==0:
				maxdepth=9999
			
			# initial url_list
			url_list=[]
			for k in scan_result:
				# it should only has root directory in each key-value pair
				url_list.append(k+scan_result[k][0])
			
			#begin discomposition
			for curdepth in range(maxdepth):
				if len(url_list)==0:
					break
				self._manager.init_task_statistics()
				if compbrute==True:
					try:
						task_granularity=4
						# generate list of subtasks 
						subtasklist=self._generate_compbrute_subtask(url_list,dirlen,charset,task_granularity)
						for cursubtask in subtasklist:
							self._manager.put_task('__dirs__',cursubtask)
					except SwarmParseException, e:
						LOG.critical('invalid directory '+str(e)+', or format error')
						raise SwarmUseException('invalid directory '+str(e)+', or format error')
				else:
					if dict=='':
						LOG.critical('directory dictionary need to be provided')
						raise SwarmUseException('directory dictionary need to be provided')
					try:
						task_granularity=1000
						# generate list of subtasks
						subtasklist=self._generate_dictbrute_subtask(url_list,dict,task_granularity)
						for cursubtask in subtasklist:
							self._manager.put_task('__dirs__',cursubtask)
					except IOError, e:
						LOG.critical('can not open dictionary for directory scan, path:%s'%(dict))
						raise SwarmUseException('can not open dictionary for directory scan, path:%s'%(dict))
				# get result
				url_list=[]
				self._manager.prepare_get_result()
				while True:
					result=self._manager.get_result()
					if result=='':
						break
					if result!='no dir or file':
						result_list=result.split(';')
						# store result into url_list for next scan 
						for x in result_list:
							if x[-1]=='/':
								url_list.append(x)
						# store result into final result
						key='/'.join(result_list[0].split('/')[:3])
						for x in result_list:
							scan_result[key].append(x[len(key):])
			# finish loop
		LOG.info('finish brute force in dir scan.')
		LOG.debug('result:%s'%scan_result)

		# use crawler.
		if enable_crawler==True:
			pass

		return scan_result

	def scan_host(self,targetl,enable_port_scan,ports):
		"""
		Decomposition domain name scan task and distribute tasks, get result from swarm.

		Returns:
			A dict using ip/domain name as keys and a dict contains port infomation as values.
			The subdict uses port number as keys and a list like [status,service,product] as values.
			For example:

			{'github.com':{80:['open','http','nginx'],443:['closed','https','unknown']},
			 'stackoverflow.com':{80:['open','http','nginx'],443['closed','https','unknown']}}
		"""
		if enable_port_scan:

			if ports=='':
				LOG.critical('at least one port should be specified if you want to scan port on target host')
				raise SwarmUseException('at least one port should be specified if you want to scan port on target host')
			
			try:
				portl=self._parse_port_list(ports)
			except SwarmParseException, e:
				LOG.critical('invalid port argument in host ports scan')
				raise SwarmUseException('invalid port argument in host ports scan')

			# just for test dir scan here
			scan_result={}
			for cur in targetl:
				scan_result[cur]={}
				for curport in portl:
					scan_result[cur][curport]=['open','http','apache']
			# end test
		
		return scan_result

	def scan_web_vul():
		pass

	def scan_host_vul():
		pass

	def try_exp():
		pass

	def try_post_exp():
		pass	

	def _generate_compbrute_subtask(self,targetlist,len_interval,charset,granularity):
		# parse interval of subdomain name length
		minlen,maxlen=self._parse_digital_interval(len_interval)
		# parse char set
		charset=self._parse_charset(charset)

		subtasklist=[]
		for cur_target in targetlist:
			begin_str=''
			if maxlen<granularity:
				begin_str=minlen*charset[0]
				end_str=maxlen*charset[-1]
				task='|'.join([cur_target,'comp',charset,begin_str,end_str])
				subtasklist.append(task)
				continue

			if minlen<granularity:
				begin_str=minlen*charset[0]
				end_str=(granularity-1)*charset[-1]
				task='|'.join([cur_target,'comp',charset,begin_str,end_str])
				subtasklist.append(task)

			bflist=generate_bflist(charset,charset[0],(maxlen-granularity+1)*charset[-1])
			for pre_str in bflist:
				begin_str=pre_str+(granularity-1)*charset[0]
				end_str=pre_str+(granularity-1)*charset[-1]
				task='|'.join([cur_target,'comp',charset,begin_str,end_str])
				subtasklist.append(task)
		return subtasklist

	def _generate_dictbrute_subtask(self,targetlist,dict_path,granularity):
		# get total number of dictionary lines
		with open(dict_path) as fp:
			sumline=sum(1 for i in fp)

		subtasklist=[]
		for cur_target in targetlist:
			# begin from fisrt line
			cur_line=1
			while True:
				# after next calculation, cur_line point to next start line 
				if (cur_line+granularity)>sumline:
					lines=sumline-cur_line+1
				else:
					lines=granularity
				task='|'.join([cur_target,'dict',dict_path,str(cur_line),str(lines)])
				subtasklist.append(task)
				# update current line 
				cur_line+=granularity
				if cur_line>sumline:
					break
		return subtasklist

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

	def _parse_port_list(self,ports):
		"""
		Parse ports string like '80|443|1-1024' into port list.
		"""
		try:
			ret=[]
			ports=ports.split('|')
			for curport in ports:
				midindex=curport.find('-')
				if midindex!=-1:
					min=int(curport[:midindex],10)
					max=int(curport[midindex+1:],10)
					if min<0 or min>65535 or max<0 or max>65535:
						raise SwarmUseException('invalid ports')
					for x in range(min,max+1):
						ret.append(x)
					continue
				curport=int(curport,10)
				if curport<0 or curport>65535:
					raise SwarmUseException('invalid ports')
				ret.append(curport)
			# remove duplicate element
			return {}.fromkeys(ret).keys()
		except Exception, e:
			raise SwarmParseException('ports')


	def _parse_digital_interval(self,interval):
		"""
		Parse digital interval like '2-13' and return (minlen,maxlen) like (2,13).
		"""
		try:
			midindex=interval.find('-')
			minlen=int(interval[:midindex],10)
			maxlen=int(interval[midindex+1:],10)
			return minlen,maxlen
		except Exception, e:
			raise SwarmParseException('len_interval')

	def _parse_charset(self,charset):
		"""
		Parse charset like 'ABC Da-d' into 'ABC Dabcd'
		"""
		try:
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
			raise SwarmParseException('charset')

	def _parse_args_for_swarm(self):
		s=''
		s=self._put_key_value(s,'m_addr',self._args.m_addr)
		s=self._put_key_value(s,'m_port',self._args.m_port)
		s=self._put_key_value(s,'authkey',self._args.authkey)
		s=self._put_key_value(s,'process_num',self._args.process_num)
		s=self._put_key_value(s,'thread_num',self._args.thread_num)
		s=self._put_key_value(s,'domain_timeout',self._args.domain_timeout)
		s=self._put_key_value(s,'dir_timeout',self._args.dir_timeout)
		s=self._put_key_value(s,'dir_not_exist',self._args.dir_not_exist)
		s=self._put_key_value(s,'dir_quick_scan',self._args.dir_quick_scan)
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

