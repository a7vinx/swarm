#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
from lib.core.exception import SwarmParseException

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

def merge_querys(url1,url2):
    """
    Merge two query params string like 'p1=param&p2=param' into one query string 
    with Deduplication. 
    """
    l1=[x.split('=')[1] for x in url1.split('&') if len(x.split('='))==2]
    l2=[x.split('=')[1] for x in url2.split('&') if len(x.split('='))==2]
    retl=copy.copy(l1)
    for x in l2:
        if x not in l1:
            retl.append(x)
    rets='=param&'.join(retl)+'=param' if len(retl)!=0 else ''
    return rets

def input2json(input):
    """
    Add double quotes in argument "input" in order to make json.loads() can execute 
    correctly.
    """
    try:
        ret=input
        readyl=['{','}',':',',','[',']','"']
        for sym in ['{','}',':',',','[',']']:
            index=ret.find(sym)
            while index!=-1:
                if index==0:
                    ret=ret[0]+'"'+ret[1:] if ret[1]!='"' else ret 
                elif index==len(ret)-1:
                    ret=ret[:-1]+'"'+ret[-1] if ret[-2]!='"' else ret
                else:
                    ret=ret[:index+1]+'"'+ret[index+1:] if ret[index+1] not in readyl else ret
                    ret=ret[:index]+'"'+ret[index:] if ret[index-1] not in readyl else ret
                # find next
                index=ret.find(sym,index+1)
        return ret
    except Exception, e:
        raise SwarmParseException('json')

