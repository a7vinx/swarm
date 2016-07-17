#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from lib.core.exception import SwarmModuleException

def get_modules():
	"""
	Returns:
		return a list consist of module name.
	Raises:
		SwarmModuleException: An error occurred when try to get modules or no available module.
	"""
	try:
		ret=[]
		content=os.listdir('./modules')
		for x in content:
			if x!='module_template' and not x.startswith(('.','__')):
				ret.append(x)
	except Exception as e:
		raise SwarmModuleException('an error occurred when try to get modules, please check modules'
			' in directory ./modules/')

	# check available module
	if len(ret)==0:
		raise SwarmModuleException('no available module')
	return ret




