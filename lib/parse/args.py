#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib.core.exception import SwarmUseException
from lib.core.exception import SwarmParseException

def parse_port_list(ports):
    """
    Parse ports string like '80;443;1-1024' into port list.

    Returns:
        A list consist of port, which type is int.
    Raises:
        SwarmParseException: An error occurred when parse ports.
    """
    try:
        ret=[]
        ports=ports.split(',')
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
        ret={}.fromkeys(ret).keys()
        ret.sort()
        return ret
    except Exception as e:
        raise SwarmParseException('ports')

def parse_digital_interval(interval):
    """
    Parse digital interval like '2-13' and return (minlen,maxlen) like (2,13).

    Returns:
        Tuple contains minlen and maxlen, which type is int.
    Raises:
        SwarmParseException: An error occurred when parse digital interval.
    """
    try:
        midindex=interval.find('-')
        minlen=int(interval[:midindex],10)
        maxlen=int(interval[midindex+1:],10)
        return minlen,maxlen
    except Exception as e:
        raise SwarmParseException('len_interval')

def parse_charset(charset):
    """
    Parse charset like 'ABC Da-d' into 'ABC Dabcd'.

    Returns:
        String like 'ABCDabcd'.
    Raises:
        SwarmParseException: An error occurred when parse charset.
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
        # LOG.debug('charset: %s'%ret)
        return ret
    except Exception as e:
        raise SwarmParseException('charset')