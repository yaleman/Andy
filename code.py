#!/usr/bin/env python


import os
import toolbox
import config


#import json


class Code( toolbox.base_plugin ):
	def __init__( self, parent ):
		toolbox.base_plugin.__init__( self, parent )
		self.pluginname = "code"

	def _filelist( self ):
		""" returns basically the results of `find .` but in an array etc."""
		filelist = []
		for (path, dirs, files) in os.walk( "."):
			for f in files:
				yield "{}/{}".format( path, f )

	def todo( self, text ):
		# search through .py files in the current folder and look for to-do's
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
				retval += "\n{}\n".format( f ) + "\n".join( lines )
				
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
				print "File: {} has unused imports: {}".format( f, ", ".join( unused ) )
				foundunused = True
		if( foundunused ):
			return "Found unused imports"
		return "All clear"
		
	def pylint( self, text ):
		""" runs pylint on all the .py files in the current codebase, skips todo's and unused imports """
		passed = []
		for f in [ f for f in self._filelist() if f.endswith( ".py" ) ]:
			output = [ line for line in toolbox.run( "pylint "+f ) if ("TODO" not in line and "Unused import" not in line and line.strip() != "" ) ]
			if len( output ) > 1:
				print "\n".join( output )
			else:
				passed.append( f )
		return "The following files passed: {}".format( ", ".join( passed ) )
		
if( __name__ == '__main__' ):
	pass

