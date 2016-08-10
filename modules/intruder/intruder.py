#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
from multiprocessing.dummy import Pool
from multiprocessing import TimeoutError
from lib.utils.utils import input2json
from lib.utils.brute import generate_bflist
from lib.utils.subtasks import generate_compbrute_subtask
from lib.utils.subtasks import generate_dictbrute_subtask
from lib.parse.args import parse_digital_interval
from lib.parse.args import parse_charset
from lib.core.exception import SwarmUseException
from lib.core.exception import SwarmParseException
from lib.core.logger import LOG

def add_cli_args(cli_parser):
    # intruder options
    intruder=cli_parser.add_argument_group('Intruder',
        "Use indicator symbol '@n@' where 'n' should be a number, like '@0@','@1@' "
        "etc to specify attack point in option 'int_target' and 'int_body'. Use "
        "'int_payload' option to specify payload used on these attack point to "
        "complete this attack.")
    intruder.add_argument('--int-target',dest='int_target',metavar='URLS',nargs='*',
            help="Use this option instead of '-t' or '-T' options to specify targets,"
                "separated by comma")
    intruder.add_argument('--int-method',dest='int_method',metavar='METHOD',
            help='Http method used in this attack')
    intruder.add_argument('--int-headers',dest='int_headers',metavar='JSON',
            help='A JSON format data.(eg: {"User-Agent":"Mozilla/5.0","Origin":"XXX"})')
    intruder.add_argument('--int-cookies',dest='int_cookies',metavar='COOKIES',
            help='Separated by comma. (eg: PHPSESSIONID:XX,token:XX)')
    intruder.add_argument('--int-body',dest='int_body',metavar='BODY',
            help='HTTP or HTTPS body. You can use indicator symbol in this option')
    intruder.add_argument('--int-payload',dest='int_payload',metavar='PAYLOAD',
            help="The format should follow '@0@:PATH,@1@:NUM-NUM:CHARSET'")
    intruder.add_argument('--int-flag',dest='int_flags',metavar='FLAGS',
            help='Separated by double comma if you have multiple flags')
    intruder.add_argument('--int-timeout',dest='int_timeout',metavar='TIME',type=float,
            help='Timeout option for intruder module')

def parse_conf(args,conf_parser):
    # intruder options
    args.int_target=conf_parser.get('Intruder','int_target')
    args.int_method=conf_parser.get('Intruder','int_method')
    args.int_headers=conf_parser.get('Intruder','int_headers')
    args.int_cookies=conf_parser.get('Intruder','int_cookies')
    args.int_body=conf_parser.get('Intruder','int_body')
    args.int_payload=conf_parser.get('Intruder','int_payload')
    args.int_flags=conf_parser.get('Intruder','int_flags')
    args.int_timeout=conf_parser.getfloat('Intruder','int_timeout')

    # in order to pass the check on args.target 
    args.target=['127.0.0.1',]
    args.int_target=args.int_target.split(',')

class Master(object):
    """
    Intruder task distributor and task result handler.

    Task format:
        Task:
        url|body|dict|dict_path|start_line|scan_lines
        url|body|comp|charset|begin_str|end_str
        Result:
        URL,PAYLOAD;URL,PAYLOAD
        nothing here
    Example:
        put task:
        https://github.com/XX.php?pw=@@@||dict|./dict/test.dict|1|1000
        http://XX.com:4040/XX.php||comp|a-z|aaa|zzz
        get result:
        https://github.com/XX.php?pw=1234,;https://github.com/XX.php?pw=1235,
        nothing here
    """
    def __init__(self, args):
        super(Master, self).__init__()
        self._args = args
        self._symnum = 0

        # common check and parse args first
        if len(args.int_target)==0:
            raise SwarmUseException('at least one target need to be provided for intruder')
        for t in args.int_target:
            if not t.startswith(('https://','http://')):
                raise SwarmUseException('unsupported scheme: '+t)
        if args.int_method.lower() not in ['get','post','head','delete','options','trace',
            'put','connect']:
            raise SwarmUseException('illegal http method')
        else:
            self._args.int_method=args.int_method.lower()
        # check headers format
        try:
            if args.int_headers!="":
                self._args.int_headers=json.loads(input2json(args.int_headers))
        except Exception as e:
            raise SwarmUseException('broken json data used in customized http headers')
        # check cookies format
        if args.int_cookies!='':
            cookiel=args.int_cookies.split(',')
            for cur in cookiel:
                if len(cur.split(':'))!=2:
                    raise SwarmUseException('cookies format error')
        # count attack points number in url and payload
        for cur_n in xrange(999):
            if args.int_body.find('@'+str(cur_n)+'@')==-1:
                find=[True if t.find('@'+str(cur_n)+'@')!=-1 else False for t in args.int_target]
                if not any(find):
                    break
            self._symnum=cur_n+1
        if self._symnum==0:
            raise SwarmUseException('at least one attack point need to be specified')
        # in case too many attack points
        if args.int_body.find('@999@')!=-1:
            raise SwarmUseException('too many attack points')
        for t in args.int_target:
            if t.find('@999@')!=-1:
                raise SwarmUseException('too many attack points')

        # parse and count attack points in payload
        if args.int_payload=='':
            raise SwarmUseException('you need to specify your payload')
        else:
            self._args.int_payload=args.int_payload.split(',')
            if len(self._args.int_payload)!=self._symnum:
                raise SwarmUseException('attack points mismatch between ones marked '
                    'and ones specified in payload')
            for index,cursym in enumerate(self._args.int_payload):
                pair=cursym.split(':')
                if pair[0]!='@'+str(index)+'@':
                    raise SwarmUseException('the number in indicator symbol should '
                        'increase continuously')

                if len(pair)==2:
                    try:
                        with open(pair[1]) as fp:
                            pass
                    except IOError as e:
                        raise SwarmUseException('can not open dictionary: '+pair[1])
                elif len(pair)==3:
                    try:
                        pair[1]=parse_charset(pair[1])
                        pair[2]=parse_digital_interval(pair[2])
                    except SwarmParseException as e:
                        raise SwarmUseException('invalid '+str(e)+'in "'+
                            self._args.int_payload[index]+'"')
                else:
                    raise SwarmUseException('payload format error, it should be like: '
                            '"@0@:PATH,@1@:NUM-NUM:CHARSET"')
                self._args.int_payload[index]=pair
        self._done=False

    def generate_subtasks(self):
        if self._done:
            return []
        subtaskl=[]
        p_taskl=[]
        for cururl in self._args.int_target:
            p_taskl.extend(self._recur_set_payloads(cururl,self._args.int_body,self._symnum-1))

        # compose two parts to generate final subtasks list
        if len(self._args.int_payload[0])==2:
            s_taskl=generate_dictbrute_subtask([''],self._args.int_payload[0][1],
                self._args.task_granularity)
        else:
            len_interval=(str(self._args.int_payload[0][2][0])+'-'+
                str(self._args.int_payload[0][2][1]))
            s_taskl=generate_compbrute_subtask([''],len_interval,
                self._args.int_payload[0][1],self._args.task_granularity)
        for curp in p_taskl:
            subtaskl.extend([curp[0]+'|'+curp[1]+curs for curs in s_taskl])

        self._done=True
        return subtaskl

    def _recur_set_payloads(self,url,body,depth):
        if depth==0:
            return [[url,body],]
        else:
            ret=[]
            replacel=[]
            if len(self._args.int_payload[depth])==2:
                with open(self._args.int_payload[depth][1]) as fp:
                    replacel.append(fp.readline())
            else:
                charset=self._args.int_payload[depth][1]
                replacel=generate_bflist(charset,
                    self._args.int_payload[depth][2][0]*charset[0],
                    self._args.int_payload[depth][2][1]*charset[-1],)

            # recursion
            for curre in replacel:
                ret.extend(self._recur_set_payloads(
                    url.replace('@'+str(depth)+'@',curre),
                    body.replace('@'+str(depth)+'@',curre),
                    depth-1)
                )
            return ret

    def handle_result(self,result):
        if result!='nothing here':
            resultl=result.split(';')
            for cur in resultl:
                curl=cur.split(',')
                self._args.coll.insert({'url':curl[0],'body':curl[1]})

    def report(self):
        all=self._args.coll.find()
        print '===================================='
        for x in all:
            print 'url: '+x['url']+'\t'+'body: '+x['body']
        print '===================================='


class Slave(object):
    """
    Real intruder that will sending payloads and check responses.

    Task format:
        Task:
        url|body|dict|dict_path|start_line|scan_lines
        url|body|comp|charset|begin_str|end_str
        Result:
        URL,PAYLOAD;URL,PAYLOAD
        nothing here
    Example:
        put task:
        https://github.com/XX.php?pw=@@@||dict|./dict/test.dict|1|1000
        http://XX.com:4040/XX.php||comp|a-z|aaa|zzz
        get result:
        https://github.com/XX.php?pw=1234,;https://github.com/XX.php?pw=1235,
        nothing here
    """
    def __init__(self, args):
        super(Slave, self).__init__()
        self._pool=Pool(args.thread_num)
        self._timeout=args.int_timeout
        self._call_method=getattr(requests,args.int_method)
        self._flags=args.int_flags.split(',,')
        if args.int_headers!="":
            self._headers=json.loads(input2json(args.int_headers))
        else:
            self._headers={}

        if args.int_cookies!='':
            cookiesl=args.int_cookies.split(',')
            self._cookies={x.split(':')[0]:x.split(':')[1] for x in cookiesl}
        else:
            self._cookies={}
        
    def do_task(self,task):
        task=task.split('|')
        if task[2]=='dict':
            result=self.dict_brute(task[0],task[1],task[3],task[4],task[5])
        else:
            result=self.complete_brute(task[0],task[1],task[3],task[4],task[5])
        return result

    def complete_brute(self,url,body,charset,begin_str,end_str):
        resultl=[]
        bflist=generate_bflist(charset,begin_str,end_str)
        for cur in bflist:
            resultl.append(self._pool.apply_async(self._request,
                args=(url.replace('@0@',cur),body.replace('@0@',cur))))
        return self._get_result(resultl)

    def dict_brute(self,url,body,dict_path,start_line,lines):
        resultl=[]
        lines=int(lines,10)
        start_line=int(start_line,10)
        with open(dict_path) as fp:
            fcontent=fp.readlines()
            for cur_index in range(lines):
                cur=fcontent[start_line+cur_index-1].strip()
                resultl.append(self._pool.apply_async(self._request,
                    args=(url.replace('@0@',cur),body.replace('@0@',cur))))
        return self._get_result(resultl)

    def _request(self,url,body):
        LOG.debug('request target: '+url)
        r=self._call_method(url,data=body,headers=self._headers,cookies=self._cookies)
        for cur_flag in self._flags:
            if r.text.find(cur_flag)!=-1:
                return url+','+body+';'
        return ''

    def _get_result(self,resultl):
        result=''
        # get result from list
        for cur in resultl:
            try:
                result+=cur.get(timeout=self._timeout)
            except TimeoutError as e:
                continue
        # deal with result
        if result=='':
            result='nothing here'
        else:
            result=result[:-1]
        return result
        
