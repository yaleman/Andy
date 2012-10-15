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


class Todo( toolbox.base_plugin ):
	def __init__( self, parent ):
		toolbox.base_plugin.__init__( self, parent )
		self.pluginname = "todo_code"

	def check( self, text ):
		#pass
		# search through .py files in the current folder and look for to-do's
		#return toolbox.run( "pwd" )
		dh = os.listdir( "." )
		retval = ""
		for f in dh:
			if f.endswith( ".py" ):
				found = False
				lines = []
				fc = open( f, 'r' ).read()
				for line in fc.split( "\n" ):
					if "#TODO" in line or "# TODO" in line:
						found = True
						lines.append( line.strip() )
				if( found ):
					retval += "\n\n{}\n".format( f ) + "\n".join( lines )
					
		return retval
if( __name__ == '__main__' ):
	pass

