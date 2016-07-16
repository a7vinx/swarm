#!/user/bin/python
# -*- coding: utf-8 -*-

import requests
import urlparse
import bs4


class Crawler(object):
	"""
	Sitemap crawler.
	Parse url in attribute href and action.
	"""
	def __init__(self):
		super(Crawler, self).__init__()
		
	def crawl_url(self,target):
		"""
		Get and parse target url, return string consist of urls which are in the same site 
		with target url.
	
		Returns:
			A string consist of url, separated by ';'. If nothing has been parsed out, return ''.
			For example:
	
			'https://github.com/blog;https://github.com/about;https://github.com/security'
		"""
		try:
			result=''		
			# get content of target
			r=requests.get(target)
			soup=bs4.BeautifulSoup(r.content,'html.parser')
			# get all tags
			hrefs=soup.find_all(href=True)
			actions=soup.find_all(action=True)
			# used for check url
			cur_netloc=urlparse.urlparse(target).netloc
			cur_dir=urlparse.urlparse(target).path
			if cur_dir[-1]!='/':
				cur_dir='/'.join(cur_dir.split('/')[:-1])
			else:
				cur_dir=cur_dir[:-1]
			cur_scheme=urlparse.urlparse(target).scheme

			for curtag in hrefs:
				result+=self._parse_url(curtag['href'],cur_scheme,cur_netloc,cur_dir)
			for curtag in actions:
				print curtag['action']
				result+=self._parse_url(curtag['action'],cur_scheme,cur_netloc,cur_dir)
			return result[:-1]
		except Exception, e:
			if result!='':
				return result[:-1]
			else:
				return ''

	def _parse_url(self,url,scheme,netloc,dir):
		"""
		Check wether target url is in the same domain(include port), and convert url into complete 
		url without params.

		Returns:
			String of complete url with ';'. if target url is not in the same domain, return '';
		"""
		o=urlparse.urlparse(url)
		# if it is a relative url
		if o.netloc=='':
			return urlparse.ParseResult(scheme,netloc,dir+o.path,'','','').geturl()+';'
		elif o.netloc==netloc:
			return urlparse.ParseResult(scheme,netloc,o.path,'','','').geturl()+';'
		else:
			return ''


