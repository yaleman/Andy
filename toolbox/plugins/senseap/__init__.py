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

class AP( toolbox.base_plugin ):
	def __init__( self, parent ):
		toolbox.base_plugin.__init__( self, parent )
		self.pluginname = "sense-ap"
		self._command_current_connection = "airport -I"
		self._command_scan = "airport -s"

	def _current_data( self, text=None ):
		data = [ line for line in toolbox.run( self._command_current_connection ) if line.startswith( "SSID" ) and line.strip() != "" ]
		data = data[0].split( ":" )[1].strip()
		if( data != "" ):
			return data
		else:
			#return "no access point"
			return False

	def current( self, text=None ):
		tmp = self._current_data()
		if not tmp:
			return "Currently disconnected"
		else:
			return "Connected to {}.".format( self._current_data() )

if( __name__ == '__main__' ):
	pass
