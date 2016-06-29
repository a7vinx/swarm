#!/user/bin/python
# -*- coding: utf-8 -*-

from IPy import IP
from lib.core.logger import LOG
from socket import getaddrinfo
from socket import gaierror


def getlist(**t):
	"""
	return integrated ip list from target list and file
	"""
	try:
		LOG.info('begin to parse target list')
		iplist=[]
		if t['target']!='':
			target=t['target']
			iplist.extend(target)

		if t['target_file']!='':
			target_file=t['target_file']
			f=open(target_file,'r')
			targets=f.read()
			iplist.extend(targets.splitlines())
			f.close()
		# unite and check
		iplist=_unite_iplist(iplist)
		LOG.info('parse completed')
		return iplist
	except ValueError, e:
		LOG.error('invalid target')
		raise
	except gaierror, e:
		LOG.error('invalid target')
		raise 
	except IOError, e:
		LOG.error('can not open target file')
		raise 

def getswarmlist(**t):
	"""
	return integrated ip&port list from swarm list and file 
	like ['127.0.0.1',80,'127.0.0.2',81]
	"""
	try:
		LOG.info('begin to parse swarm list')
		rawlist=[]
		iplist=[]
		portlist=[]
		if t['swarm']!='':
			swarm=t['swarm']
			rawlist.extend(swarm)

		if t['swarm_file']!='':
			swarm_file=t['swarm_file']
			f=open(swarm_file,'r')
			swarm=f.read()
			rawlist.extend(swarm.splitlines())
			f.close()
		iplist,portlist=_unite_swarmlist(rawlist)
		LOG.info('parse completed')
		return iplist,portlist
	except ValueError, e:
		LOG.error('invalid swarm target')
		raise
	except gaierror, e:
		LOG.error('invalid swarm target')
		raise
	except IndexError, e:
		LOG.error('invalid swarm target')
		raise
	except IOError, e:
		LOG.error('can not open swarm file')
		raise 

def _unite_swarmlist(rawlist):
	"""
	convert rawlist into ip list without domain name
	"""
	retip=[]
	retport=[]
	for x in rawlist:
		ipport=x.split(':')
		port=ipport[1]
		if int(port,10)<0 or int(port,10)>65535:
			raise ValueError('port format error')

		ip=ipport[0]
		ipl=_try_name2ip(ip)
		for x in ipl:
			# add into another list
			retip.append(x)
			retport.append(int(port,10))
	return (retip,retport)


def _unite_iplist(srclist):
	"""
	convert srclist into ip list without domain name and network segment
	"""
	ret=[]
	# can not use enumetrate() here
	for cur in srclist:
		# if this is a network segment
		if cur.find('/')!=-1:
			ret.extend(_seg2iplist(cur))
		else:
			ret.extend(_try_name2ip(cur))
	return ret

def _try_name2ip(src):
	"""
	convert src (domain name or ip) into ip list and do check meanwhile
	"""
	try:
		ret=[]
		ret.append(IP(src).strNormal())
		return ret
	# maybe it is a domain name so we have a try
	except ValueError, e:
		ret=[]
		tmp=getaddrinfo(src,None)
		for cur in tmp:
			ret.append(cur[4][0])
		return {}.fromkeys(ret).keys()
	

def _seg2iplist(seg):
	iplist=[]
	ip=IP(seg)
	for x in ip:
		iplist.append(x.strNormal())
	return iplist


	




