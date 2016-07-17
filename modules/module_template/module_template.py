#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is a template of swarm module. You can write your own module for swarm using this 
module template.

"""
def add_cli_args(cli_parser):
	pass

def parse_conf(args,conf_parser):
	pass

class Master(object):
	"""
	docstring for Master
	"""
	def __init__(self, args):
		super(Master, self).__init__()
		self._args = args	

	def generate_subtasks(self,args):
		pass

	def handle_result(self,result):
		pass

	def report(self):
		pass

class Slave(object):
	"""
	docstring for Slave
	"""
	def __init__(self, args):
		super(Slave, self).__init__()
		self._args = args

	def do_task(self,task):
		pass
		