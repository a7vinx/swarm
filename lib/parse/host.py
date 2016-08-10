#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
from IPy import IP
from lib.core.exception import SwarmNetException
from lib.core.exception import SwarmFileException
from lib.core.exception import SwarmParseException

def getlist(target='',target_file=''):
    """
    Return integrated ip and domain name list from target list and file, 
    with network segment parsed.

    Raises:
        SwarmNetException: time out when parsing target
        SwarmFileException: an error occurred when try to open target file
        SwarmParseException: an error occurred when try to parse arguments
    """
    try:
        iplist=[]
        if target!='':
            iplist.extend(target)

        if target_file!='':
            f=open(target_file,'r')
            targets=f.read()
            iplist.extend(targets.splitlines())
            f.close()
        # parse network segment and check
        iplist=_unite_list(iplist)
        return iplist
    except socket.timeout as e:    
        raise SwarmNetException('time out when parsing target')
    except IOError as e:
        raise SwarmFileException('can not open target file')
    except Exception as e:
        raise SwarmParseException('invalid address, or format error')

def getswarmlist(swarm='',swarm_file=''):
    """
    Return integrated ip and domain name list with port list from swarm list and file 
    like (['127.0.0.1','127.0.0.2','github.com'],[80,90,90]).

    Raises:
        SwarmNetException: time out when parsing target
        SwarmFileException: an error occurred when try to open target file
        SwarmParseException: an error occurred when try to parse arguments
    """
    try:
        rawlist=[]
        iplist=[]
        portlist=[]
        if swarm!='':
            rawlist.extend(swarm)

        if swarm_file!='':
            f=open(swarm_file,'r')
            swarm=f.read()
            rawlist.extend(swarm.splitlines())
            f.close()
        iplist,portlist=_unite_swarmlist(rawlist)
        return iplist,portlist
    except socket.timeout as e:
        raise SwarmNetException('time out when parsing target')
    except IOError as e:
        raise SwarmFileException('can not open target file')
    except Exception as e:
        raise SwarmParseException('invalid address, or format error')

def getiplist(srclist):
    """
    Return a complete ip list without domain name in it.
    """
    ret=[]
    for cur in srclist:
        ret.extend(_ipname2ip(cur))
    return ret

def removeip(srclist):
    """
    Remove ip in src(domain name or ip) list.
    """
    ret=[]
    for cur in srclist:
        try:
            IP(cur)
        except ValueError as e:    
            ret.append(cur)
    return ret

def _unite_swarmlist(rawlist):
    """
    Convert rawlist into ip list without domain name.
    """
    retip=[]
    retport=[]
    for x in rawlist:
        ipport=x.split(':')
        port=ipport[1]
        if int(port,10)<0 or int(port,10)>65535:
            raise ValueError('port format error')

        ip=ipport[0]
        # do check 
        _try_ipname2ip(ip)
        retip.append(ip)
        retport.append(int(port,10))
    return (retip,retport)


def _unite_list(srclist):
    """
    Convert srclist into ip and domain name list without network segment.
    """
    ret=[]
    # can not use enumetrate() here
    for cur in srclist:
        # if this is a network segment
        if cur.find('/')!=-1:
            ret.extend(_seg2iplist(cur))
        else:
            # just do check
            _try_ipname2ip(cur)
            ret.append(cur)
    return ret

def _seg2iplist(seg):
    iplist=[]
    ip=IP(seg)
    for x in ip:
        iplist.append(x.strNormal())
    return iplist

def _ipname2ip(src):
    """
    Convert src (domain name or ip) into ip list and do check meanwhile.
    """
    try:
        retip=[]
        retip.append(IP(src).strNormal())
        return retip
    # maybe it is a domain name so we have a try
    except ValueError as e:
        retip=[]
        tmp=socket.getaddrinfo(src,None)
        for cur in tmp:
            retip.append(cur[4][0])
        return {}.fromkeys(retip).keys()

def _try_ipname2ip(src):
    try:
        IP(src)
    except ValueError as e:
        # maybe it is a domain name so we have a try
        socket.getaddrinfo(src,None)


