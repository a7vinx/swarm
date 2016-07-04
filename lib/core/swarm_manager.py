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
