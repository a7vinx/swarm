#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymongo
import time
from lib.core.exception import SwarmDBException

def init_db(addr,port,modname):
    """
    Returns:
        A db Object and a collection Object of Mongodb.
    Raises:
        SwarmDBException: An error occurred when try to init db.
    """
    try:
        timeformat='%Y_%m_%d_%H_%M_%S'
        dbclient = pymongo.MongoClient(addr, port)
        return dbclient.swarm,dbclient.swarm[modname+'_'+time.strftime(timeformat,time.localtime())]
    except Exception, e:
        raise SwarmDBException('Failed to connect to MongoDB server. Error info:'+str(e))
    