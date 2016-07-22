#!/usr/bin/env python
# -*- coding: utf-8 -*-

class SwarmBaseException(Exception):
	pass

class SwarmUseException(SwarmBaseException):
	pass

class SwarmNetException(SwarmBaseException):
	pass

class SwarmParseException(SwarmBaseException):
	pass

class SwarmModuleException(SwarmBaseException):
	pass

class SwarmFileException(SwarmBaseException):
	pass

class SwarmDBException(SwarmBaseException):
	pass