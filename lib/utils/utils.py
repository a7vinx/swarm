#!/usr/bin/env python
# -*- coding: utf-8 -*-


def merge_ports(portl):
	"""
	Args:
		portl(list): a list consist of int value represents ports.
	Returns:
		A string like ['2','4-100','200']
	"""
	ret=[]
	index=0
	while index<len(portl)-1:
		if portl[index]+1==portl[index+1]:
			begin=index
			end=index
			while index<len(portl)-1 and portl[index]+1==portl[index+1]:
				index+=1
				end=index
			ret.append(str(portl[begin])+'-'+str(portl[end]))
		else:
			ret.append(str(portl[index]))
			index+=1
	if len(ret)==0 and len(portl)!=0:
		ret.append(str(portl[-1]))

	if ret[-1].find('-')==-1:
		ret.append(str(portl[-1]))
	return ret