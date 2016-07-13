#!/user/bin/python
# -*- coding: utf-8 -*-

class SwarmBaseException(Exception):
	pass

class SwarmUseException(SwarmBaseException):
	pass

class SwarmNetException(SwarmBaseException):
	pass

class SwarmParseException(SwarmBaseException):
	pass
