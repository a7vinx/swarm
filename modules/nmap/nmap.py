#!/usr/bin/env python
# -*- coding: utf-8 -*-

from libnmap.process import NmapProcess
from libnmap.parser import NmapParser, NmapParserException
import argparse

from lib.core.exception import SwarmUseException
from lib.core.exception import SwarmParseException
from lib.parse.args import parse_port_list
from lib.utils.utils import merge_ports

def add_cli_args(cli_parser):
    # nmap module options
    nmap=cli_parser.add_argument_group('Nmap Module',
            'These options can be used customize nmap action on slave hosts')
    nmap.add_argument('--nmap-ports',dest='nmap_ports',metavar='PORTS',
            help="Support format like '80,443,3306,1024-2048'")
    nmap.add_argument('--nmap-top-ports',dest='nmap_top_ports',metavar='NUM',type=int,
            help='Scan <number> most common ports')
    nmap.add_argument('--nmap-ops',dest='nmap_options',nargs=argparse.REMAINDER,
            help="Nmap options list in nmap’s man pages, this should be the last in cli args")

def parse_conf(args,conf_parser):
    # nmap module options
    args.nmap_ports=conf_parser.get('Nmap Module','nmap_ports')
    args.nmap_top_ports=conf_parser.getint('Nmap Module','nmap_top_ports')
    args.nmap_options=conf_parser.get('Nmap Module','nmap_options')
    if args.nmap_options!='':
        args.nmap_options=args.nmap_options.split()

class Master(object):
    """
    nmap module task distributor and task result handler.

    Task Format:
        Task:
        target|port list
        Result:
        target|XML string wait for parse
    Example:
        put task:
        github.com|-p 1,2,3,4,5,6
        github.com|--top-ports 100
        get result:
        github.com|<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE nmaprun>\n<?xml-stylesheet...
    """
    def __init__(self, args):
        super(Master, self).__init__()
        self._args = args
        self._done = False

    def generate_subtasks(self):
        if self._done:
            return []
        # check wether exists option in nmap option group 'PORT SPECIFICATION' or 
        # 'TARGET SPECIFICATION'
        legall=['-sL','-sn','-Pn','-PS','-PA','-PU','-PY','-PE','-PP','-PM','-PO','-n','-R',
            '--dns-servers','--system-dns','--traceroute','-sS','-sT','-sA','-sW','-sM','-sU',
            '-sN','-sF','-sX','--scanflags','-sI','-sY','-sZ','-sO','-b','-sV','--version-intensity',
            '--version-light','--version-all','--version-trace','-sC','--script','--script-args',
            '--script-args-file','--script-trace','--script-updatedb','--script-help','-O',
            '--osscan-limit','--osscan-guess','-T','--min-hostgroup','--max-hostgroup','--min-parallelism',
            '--max-parallelism','--min-rtt-timeout','--max-rtt-timeout','--initial-rtt-timeout',
            '--max-retries','--host-timeout','--scan-delay','--max-scan-delay','--min-rate','--max-rate',
            '-f','--mtu','-D','-S','-e','-g','--source-port','--proxies','--data','--data-string',
            '--data-length','--ip-options','--ttl','--spoof-mac','--badsum','-6','-A','--datadir',
            '--send-eth','--send-ip','--privileged','--unprivileged']
        for cur in self._args.nmap_options:
             resultl=[cur.startswith(x) for x in legall]
             if not (True in resultl):
                raise SwarmUseException("not supported nmap option")

        subtaskl=[]
        # generate subtask
        if self._args.nmap_top_ports!=0:
            nmap_top_ports='--top-ports '+str(self._args.nmap_top_ports)
            for curhost in self._args.target_list:
                subtaskl.append(curhost+'|'+nmap_top_ports)

        elif self._args.nmap_ports!='':
            # maybe it need to be decomposited
            try:
                portl=parse_port_list(self._args.nmap_ports)
                for curhost in self._args.target_list:
                    index=0
                    while index<len(portl):
                        subtaskl.append(curhost+'|'+'-p '+
                            ','.join(merge_ports(portl[index:index+self._args.task_granularity*500])))
                        index+=self._args.task_granularity*500
            except SwarmParseException as e:
                raise SwarmUseException('illeagal port format in nmap_ports')
        else:
            raise SwarmUseException('at least one port need to be provided')
        # mark
        self._done = True
        return subtaskl

    def handle_result(self,result):
        # store it in mongodb
        resultl=result.split('|')
        if resultl[1]!='f':
            self._args.coll.insert({'host':resultl[0],'result':resultl[2]})

    def report(self):
        down_host=0
        for curhost in self._args.target_list:
            host_infol=self._args.coll.find({'host':curhost})
            # first print host info
            nmap_report=NmapParser.parse(str(host_infol[0]['result']))
            if nmap_report.hosts[0].status=='up':
                print '====================== '+curhost+' ======================'
                print 'Host is %s'%nmap_report.hosts[0].status
                # print ports info
                print("  PORT     STATE         SERVICE")
                for cur_info in host_infol:
                    nmap_report=NmapParser.parse(str(cur_info['result']))
                    for serv in nmap_report.hosts[0].services:
                        pserv = "{0:>5s}/{1:3s}  {2:12s}  {3}".format(
                        str(serv.port),
                        serv.protocol,
                        serv.state,
                        serv.service)
                        if len(serv.banner):
                            pserv += " ({0})".format(serv.banner)
                        print pserv
            else:
                down_host+=1
        print '=========================================================='
        print 'Not shown: '+str(down_host)+' down host'
        print '=========================================================='

class Slave(object):
    """
    Task Format:
        Task:
        target|port list
        Result:
        target|XML string wait for parse
    Example:
        put task:
        github.com|-p 1,2,3,4,5,6
        github.com|--top-ports 100
        get result:
        github.com|<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE nmaprun>\n<?xml-stylesheet...
    """
    def __init__(self, args):
        super(Slave, self).__init__()
        self._args = args

    def do_task(self,task):
        """
        TODO: multiple ip address for same domain name
        """
        try:
            taskl=task.split('|')
            nmap_task=NmapProcess(taskl[0],taskl[1]+' '+' '.join(self._args.nmap_options))
            rc=nmap_task.run()
            if rc!=0:
                return '|'.join([taskl[0],'f',str(rc)+' '+nmap_task.stderr])
            return '|'.join([taskl[0],'s',nmap_task.stdout])
        # if there is no nmap on current host, quit quietly
        except EnvironmentError, e:
            raise SwarmUseException(str(e))

        


