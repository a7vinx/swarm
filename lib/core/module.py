#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import modules
import pkgutil
from lib.core.exception import SwarmModuleException

def get_modules():
	"""
	Returns:
		return a list consist of module name.
	Raises:
		SwarmModuleException: An error occurred when try to get modules or no available module.
	"""
	try:
		s=os.path.dirname(modules.__file__)
		ret=[name for _, name, _ in pkgutil.iter_modules([s])]
	except Exception as e:
		raise SwarmModuleException('an error occurred when try to get modules, please check'
			' modules of swarm')

	# check available module
	if len(ret)==0:
		raise SwarmModuleException('no available module')
	return ret




