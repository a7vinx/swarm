#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

timeformat='%H:%M:%S'

def begin_banner():
    print ''
    print '[*] swarm starting at '+time.strftime(timeformat,time.localtime())
    print ''

def end_banner():
    print ''
    print '[*] swarm shutting down at '+time.strftime(timeformat,time.localtime())
    print ''