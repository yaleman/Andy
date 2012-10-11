#!/usr/bin/env python

#try:
#	import pexpect
#except ImportError:
#	print "Couldn't load pexpect"
#import re
import os
import toolbox
import config


#import json


class Todo( config.base_plugin ):
	def __init__( self, config = config ):
                config.base_plugin.__init__( self )
		self._config = config
		self.pluginname = "sense-todo"

	def check( self, text ):
		#pass
		# search through .py files in the current folder and look for to-do's
		#return toolbox.run( "pwd" )
		dh = os.listdir( "." )
		for f in dh:
			if f.endswith( ".py" ):
				print f
if( __name__ == '__main__' ):
	pass

