#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import time
import multiprocessing
import importlib
import json
import argparse
import threading
from lib.core.logger import LOG
from lib.core.manager import SSwarmManager

class SSwarm(object):
    """
    A role of slave in the distributed system.
    """
    def __init__(self,s_port):
        super(SSwarm, self).__init__()
        self._s_port=s_port
        self._args=argparse.Namespace()

    def get_parse_args(self):
        # first receive args
        args=self._receive_master()
        sync_flag=args[-8:]
        args=args[:-8]
        self._parse_args(args)
        LOG.debug('complete parsing args')

        if sync_flag=='__SYNC__':
            # do data sync here
            LOG.debug('begin to synchronize data...')
            self._sync_data()
            LOG.debug('data synchronize completed')

    def get_do_task(self):
        proc=[]
        if self._args.process_num==0:
            for cur in range(multiprocessing.cpu_count()):
                p=multiprocessing.Process(target=self._get_do_task_proc)
                p.start()
                proc.append(p)
        else:
            for cur in range(self._args.process_num):
                p=multiprocessing.Process(target=self._get_do_task_proc)
                p.start()
                proc.append(p)
        # start a new thread to listen command from master host
        # use daemon argtment so we need not to wait for this thread to exit
        t=threading.Thread(target=self._response_master)
        t.daemon=True
        t.start()
        for cur in proc:
            cur.join()
        LOG.debug('task completed')

    def _get_do_task_proc(self):
        self._manager=SSwarmManager(address=(self._args.m_addr, self._args.m_port),
                authkey=self._args.authkey)

        LOG.debug('load module: '+self._args.mod)
        LOG.debug('begin to get and do task...')
        try:
            module=importlib.import_module('modules.'+self._args.mod+'.'+self._args.mod)
        except ImportError as e:
            raise SwarmModuleException('an error occured when load module:'+self._args.mod)
        # create Slave class of this module
        mod_slave=getattr(module,'Slave')(self._args)
    
        while True:
            flag,task=self._manager.get_task()
            if flag=='__off__':
                break
            # else use module to do task
            result=mod_slave.do_task(task)
            self._manager.put_result(result)

    def _parse_args(self,args):
        dict=json.loads(args)
        for k,v in dict.items():
            LOG.debug('set self._args.'+k+' => '+str(v))
            setattr(self._args,k,v)

    def _sync_data(self):
        print self._receive_master()
        print self._receive_master()
        # TODO: do data sync here
        pass

    def _response_master(self):
        while True:
            self._receive_master()

    def _receive_master(self):
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        # incase 'Address already in use error'
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('',self._s_port))
        LOG.debug('listen on port:%d'%self._s_port)
        s.listen(1)
        sock, addr=s.accept()
        LOG.debug('receive from master host...')
        buff=''
        while True:
            d=sock.recv(4096)
            buff+=d
            if d.find('__EOF__')!=-1:
                break
        sock.send('ack')
        sock.close()
        s.close()
        # cut off last __EOF__
        buff=buff[:-7]
        # return to origin args
        buff=buff.replace('__EOF___','__EOF__')
        return buff
