#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib.parse.args import parse_digital_interval
from lib.parse.args import parse_charset
from lib.utils.brute import generate_bflist

def generate_compbrute_subtask(targetlist,len_interval,charset,granularity):
    """
    Format:
        target|comp|charset|begin_str|end_str
    """
    # convert granularity
    granularity+=2

    # parse interval of subdomain name length
    minlen,maxlen=parse_digital_interval(len_interval)
    # parse char set
    charset=parse_charset(charset)

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

def generate_dictbrute_subtask(targetlist,dict_path,granularity):
    """
    Format:
        target|dict|dict_path|start_line|scan_lines
    Raises:
        IOError: error when try to open target dict
    """
    # convert granularity
    granularity=10**(granularity+1)

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
