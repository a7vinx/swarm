#!/usr/bin/env python
# -*- coding: utf-8 -*-

def draw_sitemap(contentl):
	"""
	Args:
		contentl: A mongodb cursor object which should has key 'domain','url','method',
		'content_type','params'

	"""
	# contentlist.sort(cmp=)
	if contentl.count()==0:
		print 'nothing find here'
		return
	urll=[]
	for cur in contentl:
		re_url='/'+'/'.join(cur['url'].split('/')[3:])
		urll.append(re_url.split('?')[0])
	urll={}.fromkeys(urll).keys()
	urll.sort()
	for cur in urll:
		print cur
