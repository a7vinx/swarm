#!/usr/bin/env python
# -*- coding: utf-8 -*-

def draw_sitemap(contentl):
	"""
	Input format:

	"""
	# contentlist.sort(cmp=)
	for cur in contentl:
		print cur['url']
		print cur['method']
		print cur['content_type']
		print cur['params']
		print ''
