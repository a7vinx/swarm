#!/usr/bin/env python
# -*- coding: utf-8 -*-

def generate_bflist(charset,begin_str='',end_str=''):
    """
    Use chars in charset to generate string list used for brute force.
    No check here.
    """
    ret=[]
    maxlen=len(end_str)
    index_list=[-1 for x in range(maxlen)]
    end_list=[-1 for x in range(maxlen)]    
    for index,cur in enumerate(reversed(begin_str)):
        index_list[index]=charset.find(cur)
    for index,cur in enumerate(reversed(end_str)):
        end_list[index]=charset.find(cur)
    
    while True:
        ret.append(_indexlist2str(charset,index_list))
        index_list[0]+=1
        # check carry
        for cur in range(maxlen):
            if index_list[cur]==len(charset):
                if cur==maxlen-1:
                    break
                index_list[cur+1]+=1
                index_list[cur]=0
        # check end
        if index_list==end_list:
            # convert the last
            ret.append(_indexlist2str(charset,index_list))
            break
    return ret

def _indexlist2str(charset,index_list):
    cur_str=''
    for x in reversed(index_list):
        if x!=-1:
            cur_str+=charset[x]
    return cur_str
