#!/usr/bin/env python


import os
import toolbox
import config


#import json


class Plugin( toolbox.base_plugin ):
	def __init__( self, parent ):
		""" code is supposed to be able to allow the system to self-check """
		toolbox.base_plugin.__init__( self, parent )
		self.pluginname = "code"

	def _filelist( self ):
		""" returns basically the results of `find .` but in an array etc."""
		for (path, dirs, files) in os.walk( "."):
			for f in files:
				yield "{}/{}".format( path, f )

	def todo( self, text ):
		""" will will search through .py files in the current folder and look for to-do's in the code """
		retval = ""
		for f in [ f for f in self._filelist() if f.endswith( ".py" )]:
			found = False
			lines = []
			fc = open( f, 'r' ).read()
			for line in fc.split( "\n" ):
				if line.strip().startswith( "# TODO" ) or line.strip().startswith( "#TODO" ):
					found = True
					lines.append( line.strip() )
			if( found ):
				retval += "\n\n{}\n".format( f ) + "\n".join( lines )
				
		return retval

	def unusedimports( self, text ):
		""" does a pretty good job of trying to find unused imports in the codebase """
		foundunused = False
		# go through every .py file in the codebase
		for f in [ f for f in self._filelist() if f.endswith( ".py" )]:
			imports = []
			unused = []
			file_contents = open( f, 'r' ).read()
			# check for imports
			for line in file_contents.split( "\n" ):
				if line.strip().startswith( "import " ):
					imports.append( line.split()[1] )
			# check if the import seems to be used
			for i in sorted( imports ):
				if " {}.".format( i ) not in file_contents:
					unused.append( i )
			# report on it for the file
			if( len( unused ) > 0 ):
				print( "File: {} has unused imports: {}".format( f, ", ".join( unused ) ) )
				foundunused = True
		if( foundunused ):
			return "Found unused imports"
		return "All clear"
		
	def pylint( self, text ):
		""" runs pylint on all the .py files in the current codebase, skips todo's and unused imports """
		passed = []
		e_raised = False
		for f in [ f for f in os.listdir( "." ) if f.endswith( ".py" ) ]:
			output = [ line for line in toolbox.run( "pylint "+f ).split("\n") if ("TODO" not in line and "Unused import" not in line and line.strip() != "" ) ]
			if len( output ) > 1:
				toprint = "\n".join( output )
				if( "E:" in toprint ):
					e_raised = True
				print( toprint )
			else:
				passed.append( f )
		if e_raised:
			print( "*** ERRORS RAISED" )
		return "The following files passed: {}".format( ", ".join( passed ) )

		
if( __name__ == '__main__' ):
	pass

