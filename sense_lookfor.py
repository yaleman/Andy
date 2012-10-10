#!/usr/bin/env python

try:
	import pexpect
except ImportError:
	print "Couldn't load pexpect"
import re
import toolbox
import config


#TODO add sources
#TODO add searches based on sources
#TODO add auto-disable based on sense-ap?

class LookFor( config.base_plugin ):
	def __init__( self, config=config ):
		self._config = config
		self.pluginname = "sense_lookfor"
		


if( __name__ == '__main__' ):
	pass
