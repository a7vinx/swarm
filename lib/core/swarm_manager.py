#!/user/bin/python
# -*- coding: utf-8 -*-

import multiprocessing
from multiprocessing.managers import BaseManager

class SwarmManager(BaseManager):
	"""docstring for SwarmManager"""
	def __init__(self,address=None,authkey=None):
		super(SwarmManager, self).__init__(address=address,authkey=authkey)
		self._task_queue=multiprocessing.Queue()
		self._result_queue=multiprocessing.Queue()
		SwarmManager.register('get_task_queue',callable=lambda:self._task_queue)
		SwarmManager.register('get_result_queue',callable=lambda:self._result_queue)



# class CmdObject(object):
# 	"""docstring for CmdObject"""
# 	def __init__(self):
# 		super(CmdObject, self).__init__()
# 		self._swarm_num=0
# 		self._cmd=''
# 		self._cmd_is_valid=False

# 	def getcmd():
# 		self._swarm_num+=1
# 		return self._cmd

# 	def setcmd(new_cmd):
# 		self._cmd=new_cmd
# 		self._swarm_num=0

# 	def get_swarm_num():
# 		return self._swarm_num