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


class Plugin( toolbox.base_plugin ):
	def __init__( self, parent ):
		toolbox.base_plugin.__init__( self, parent )
		self.pluginname = "sense-ap"
		self._command_current_connection = "airport -I"
		self._command_scan = "airport -s"

	def _current_data( self, text=None ):
		""" returns the current access point that the computer is connected to """
		cmdoutput = toolbox.run( self._command_current_connection )
		cmdoutput = cmdoutput.split( "\n" )
		data = [ line.strip() for line in cmdoutput if line.strip().startswith( "SSID" ) and line.strip() != "" ]
		if data:
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
			return "Connected to {}.".format( tmp )

if( __name__ == '__main__' ):
	pass
