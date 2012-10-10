#!/usr/bin/env python

#try:
#	import pexpect
#except ImportError:
#	print "Couldn't load pexpect"
#import re
import toolbox
import config


#import json

#TODO check what AP's we're connected to (maybe on a timer?)
#TODO be able to respond about this

class AP( config.base_plugin ):
	def __init__( self, config = config ):
		self._config = config
		self.pluginname = "sense-ap"
		self._command_current_connection = "airport -I"
		self._command_scan = "airport -s"

	def current( self, text ):
		return "\n".join( [ line for line in toolbox.run( self._command_current_connection ) if line.startswith( "SSID" ) ] )

if( __name__ == '__main__' ):
	pass
