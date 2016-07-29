#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import urlparse
import bs4
import json
import time
from multiprocessing.dummy import Pool
from multiprocessing import TimeoutError
from lib.core.logger import LOG
from lib.parse.args import parse_port_list
from lib.core.exception import SwarmUseException
from lib.utils.utils import merge_querys
from lib.utils.sitemap import draw_sitemap

def add_cli_args(cli_parser):
	sitemap=cli_parser.add_argument_group('Sitemap Crawler',
		'These options can be used to customize sitemap crawler, not support js parse yet')
	sitemap.add_argument('--map-seed',dest='map_seed',metavar='SEED',
			help='Separated by comma if you have multiple seeds')
	sitemap.add_argument('--map-http-port',dest='map_http_port',metavar='PORT',
			help="Separated by comma if you need multiple ports")
	sitemap.add_argument('--map-https-port',dest='map_https_port',metavar='PORT',
			help="Separated by comma if you need multiple ports")
	sitemap.add_argument('--map-cookies',dest='map_cookies',metavar='COOKIES',
			help='Separated by comma if you have multiple cookies')
	sitemap.add_argument('--map-interval',dest='map_interval',metavar='TIME',type=float,
			help='Interval time between two request')
	sitemap.add_argument('--map-timeout',dest='map_timeout',metavar='TIME',type=float,
			help='Timeout option for sitemap crawler')

def parse_conf(args,conf_parser):
	args.map_seed=conf_parser.get('Sitemap Crawler','map_seed')
	args.map_http_port=conf_parser.get('Sitemap Crawler','map_http_port')
	args.map_https_port=conf_parser.get('Sitemap Crawler','map_https_port')
	args.map_cookies=conf_parser.get('Sitemap Crawler','map_cookies')
	args.map_interval=conf_parser.getfloat('Sitemap Crawler','map_interval')
	args.map_timeout=conf_parser.getfloat('Sitemap Crawler','map_timeout')

class Master(object):
	"""
	Sitemap crawler task distributor and task result handler.

	Task Format:
		Task:
		URL,METHOD,CONTENT-TYPE,PARAMS|URL,METHOD,CONTENT-TYPE,PARAMS
		Result:
		URL,METHOD,CONTENT-TYPE,PARAMS;URL,METHOD,CONTENT-TYPE,PARAMS
	Example:
		Put task:
		http://XX.com/XXX.php,post,multipart/form-data,param1=XX&param2=XX
		Get result:
		end
		http://XX.com/XXX.php?param1=XX&param2=XX,post,multipart/form-data,param3=XX

	"""
	def __init__(self, args):
		super(Master, self).__init__()
		self._args = args	

		# parse crawler seeds
		if self._args.map_seed=='':
			seedl=['/',]
		else:
			seedl=['/'+x for x in self._args.map_seed.split(',')]

		# check cookies format
		if self._args.map_cookies!='':
			cookiel=self._args.map_cookies.split(',')
			for cur in cookiel:
				if len(cur.split(':'))!=2:
					raise SwarmUseException('cookies format error')
		
		# parse port list
		http_portl=[]
		https_portl=[]
		# just used for check validity here
		try:
			if self._args.map_http_port!='':
				http_portl=parse_port_list(self._args.map_http_port)
			if self._args.map_https_port!='':
				https_portl=parse_port_list(self._args.map_https_port)
		except SwarmParseException as e:
			raise SwarmUseException('invalid http or https port argument in sitemap crawler')

		# generate initial domain for final result report
		# it should prepare a list contains valid domain seed like:
		# ['http://github.com:81','http://XX.com:80','https://github.com:9090']
		self._doml=[]
		for curhost in self._args.target_list:
			for curport in http_portl:
				self._doml.append('http://'+curhost+':'+str(curport))
			for curport in https_portl:
				self._doml.append('https://'+curhost+':'+str(curport))
		
		# generate inital url list wait to be crawled
		self._waitl=[]
		for curdom in self._doml:
			for curseed in seedl:
				self._waitl.append(curdom+curseed+',get,,')


	def generate_subtasks(self):
		if len(self._waitl)==0:
			return []

		# generate subtask list
		subtaskl=[]
		for cur in range(0,len(self._waitl),self._args.task_granularity*4):
			subtaskl.append('|'.join(self._waitl[cur:cur+self._args.task_granularity*4]))
		self._waitl=[]
		return subtaskl

	def handle_result(self,result):
		if result!='end':
			resultl=result.split(';')
			for ret in resultl:
				# first check duplicate
				retl=ret.split(',')
				returl=retl[0].split('?')[0]
				retquery=retl[0].split('?')[1] if len(retl[0].split('?'))==2 else ''
				dup=self._args.coll.find_one({'url':returl})
				# if it duplicate, update query params and do not add it into queue
				if dup!=None:
					merged=merge_querys(retquery,dup['query'])
					self._args.coll.update({'url':returl},{'$set':{'query':merged}})
					continue
				# else insert into database and append to waiting list
				key='/'.join(retl[0].split('/')[:3])
				self._args.coll.insert({'domain':key,'url':returl,'query':retquery,
					'method':retl[1],'content_type':retl[2],'params':','.join(retl[3:])})
				# if it ends with '.jpg','.png' etc.
				if returl.split('.')[-1] not in ['gif','jpg','jpeg','png','bmp','doc','js']:
					self._waitl.append(ret)

	def report(self):
		for curdom in self._doml:
			contentl=self._args.coll.find({'domain':curdom})
			print '================== '+curdom+' ======================'
			draw_sitemap(contentl)
		print '==================================================='


class Slave(object):
	"""
	Sitemap crawler.

	Task Format:
		Task:
		URL,METHOD,CONTENT-TYPE,PARAMS|URL,METHOD,CONTENT-TYPE,PARAMS
		Result:
		URL,METHOD,CONTENT-TYPE,PARAMS;URL,METHOD,CONTENT-TYPE,PARAMS
	Example:
		Put task:
		http://XX.com/XXX.php,post,multipart/form-data,param1=XX&param2=XX
		Get result:
		end
		http://XX.com/XXX.php?param1=XX&param2=XX,post,multipart/form-data,param3=XX

	"""
	def __init__(self, args):
		super(Slave, self).__init__()
		self._pool=Pool(args.thread_num)
		self._timeout=args.map_timeout
		self._t_interval=args.map_interval
		# parse cookies
		if args.map_cookies!='':
			cookiesl=args.map_cookies.split(',')
			for cur in cookiesl:
				cur.split(':')
			self._cookies={x.split(':')[0]:x.split(':')[1] for x in cookiesl}
		else:
			self._cookies={}

	def do_task(self,task):
		taskl=task.split('|')
		resultl=[]
		for subtask in taskl:
			argsl=subtask.split(',')
			resultl.append(self._pool.apply_async(self.crawl_url,args=(argsl[0],argsl[1],argsl[2],argsl[3])))
			time.sleep(self._t_interval)
		retl=self._get_resultl(resultl)
		return self._proc_result(retl)

	def crawl_url(self,target,method,content_type,params):
		"""
		Get and parse target url, return string consist of urls which are in the same site 
		with target url.

		Args:
			target(string): URL (include query params of GET method)
			method(string): http method name
			content_type(string): it should be one of these:
						empty string
						'multipart/form-data'
						'text/xml'
						'application/json'
			params(string): params

		Returns:
			A list consist of sublist, which has format of [URL,METHOD,CONTENT-TYPE,PARAMS], 
			For example:
	
			[['http://XX.com/XXX.php?param1=XX','post','multipart/form-data',
			'{param2:XX,param3:XX}'],[,get,,]]
		"""
		try:
			result=[]		

			# first check url, if it redirect to another domain or this url is not valid, return.
			r=requests.head(target,cookies=self._cookies)
			if not self._check_exist_code(r.status_code):
				if 'Location' in r.headers.keys():
					srcdom='/'.join(target.split('/')[:3])
					dstdom='/'.join(r.headers['Location'].split('/')[:3])
					if srcdom==dstdom:
						# parse this redirected url
						parsed=urlparse.urlparse(r.headers['Location'])
						return self.crawl_url(parsed.scheme+'//'+parsed.netloc+parsed.path,
							'get','',parsed.query)
					else:
						return ''

			# get content of response from target url 
			http_method=getattr(requests,method)
			if content_type=='multipart/form-data':
				r=http_method(target,files=json.loads(params),cookies=self._cookies)
			else:
				r=http_method(target,data=params,cookies=self._cookies)
			
			# get all useful tags
			soup=bs4.BeautifulSoup(r.content,'html.parser')
			hrefs=soup.find_all(href=True)
			actions=soup.find_all(action=True)
			srcs=soup.find_all(src=True)
			for curtag in hrefs:
				if curtag['href'].startswith('javascript:'):
					continue
				parsed_url=self._parse_url(curtag['href'],target)
				result.append([parsed_url,'get','',''])
			for curtag in srcs:
				parsed_url=self._parse_url(curtag['src'],target)
				result.append([parsed_url,'get','',''])
			for curtag in actions:
				parsed_url=self._parse_url(curtag['action'],target)
				if parsed_url!='':
					# deal with form method, content type and params
					params=''
					curtag['enctype']=curtag['enctype'] if curtag.attrs.has_key('enctype') else ''
					# attention here, pass attrs argument to find_all instead of 'name=True'
					names=curtag.find_all(attrs={'name':True})
					if curtag['enctype']=='application/json' or curtag['enctype']=='multipart/form-data':
						p_dict={}
						for name in names:
							p_dict[name['name']]='param'
						params=json.dumps(p_dict)
					else:
						for name in names:
							params=params+name['name']+'=param&'
						params=params[:-1]
					curtag['method']=curtag['method'].lower() if curtag.attrs.has_key('method') else 'get'
					result.append([parsed_url,curtag['method'],
						curtag['enctype'],params])
			
			return result
		except Exception as e:
			return result

	def _parse_url(self,dst,src):
		"""
		Check wether target url 'dst' is in the same domain(include port) with url 'src', and 
		convert url into complete url without params.

		Returns:
			String of complete url with query params if it has. if target url is not in the 
			same domain, return '';
		"""
		LOG.debug('detecting url: '+dst)
		s_parsed=urlparse.urlparse(src)
		s_scheme=s_parsed.scheme
		s_netloc=s_parsed.netloc
		s_cur_dir=s_parsed.path
		if s_cur_dir[-1]!='/':
			s_cur_dir='/'.join(s_cur_dir.split('/')[:-1])
		else:
			s_cur_dir=s_cur_dir[:-1]

		d_parsed=urlparse.urlparse(dst)
		d_scheme=d_parsed.scheme
		if d_parsed.netloc.find(':')==-1 and d_parsed.netloc!='':
			if d_scheme=='http':
				d_netloc=d_parsed.netloc+':80'
			elif d_scheme=='https':
				d_netloc=d_parsed.netloc+':443'
			elif d_scheme=='':
				d_netloc=d_parsed.netloc+':80' if s_scheme=='http' else d_parsed.netloc+':443'
			else:
				d_netloc=d_parsed.netloc
		else:
			d_netloc=d_parsed.netloc
		# add '/' as prefix if the path does not starts with '/'
		if d_parsed.path!='':
			d_path='/'+d_parsed.path if d_parsed.path[0]!='/' else d_parsed.path
		else:
			d_path='/'
		d_query=d_parsed.query
		
		# if it is a relative url
		if d_netloc=='':
			return urlparse.ParseResult(s_scheme,s_netloc,s_cur_dir+d_path,'',d_query,'').geturl()
		elif d_netloc==s_netloc and (d_scheme==s_scheme or d_scheme==''):
			return urlparse.ParseResult(s_scheme,s_netloc,d_path,'',d_query,'').geturl()
		else:
			return ''
		
	def _get_resultl(self,resultl):
		retl=[]
		# get result from eflist
		for cur in resultl:
			try:
				retl.extend(cur.get(timeout=self._timeout))
			except TimeoutError as e:
				continue
		return retl

	def _proc_result(self,resultl):
		"""
		Deduplicate result list and return result string.
		"""
		rets=''
		r_url=''
		r_querys=''
		resultl.sort()

		for cur in resultl:
			if len(cur)!=4 or cur[0]=='':
				continue

			cururl=cur[0].split('?')[0]
			curquerys=cur[0].split('?')[1] if len(cur[0].split('?'))==2 else ''
			if cururl==r_url:
				r_querys=merge_querys(curquerys,r_querys)
			else:
				if r_url!='':
					r_qurl=r_url+'?'+r_querys if r_querys!='' else r_url
					rets+=','.join([r_qurl,cur[1],cur[2],cur[3]])
					rets+=';'
				r_url=cururl
				r_querys=curquerys

		rets='end' if rets=='' else rets[:-1]
		return rets

	def _check_exist_code(self,code):
		if code<300 or code==401 or code==403:
			return True
		return False

