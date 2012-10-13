#!/usr/bin/env python

try:
	import pexpect
except ImportError:
	print "Couldn't load pexpect"
import re
import toolbox
import config
import os, pickle

tasklet_idea = """
tasklet

uri:[hash] = uri (http://www.google.com)

data = download contnts from uri:[hash]


regex:[hash] = "(<?P=trtotal\<tr(?P=trinner.*)\>(?P=trcontents)</tr>)" etc
re.compile( regex:[hash] )
tr's = apply the regex to the data
"""

class LookFor( config.base_plugin ):
	def __init__( self, parent, filename, config=config ):
		config.base_plugin.__init__( self, parent )
		self._config = config
		self.pluginname = "sense_lookfor"
		self._data = { 'uris' : {}, 'tasks' : {} }
		self._filename = filename
		self.load()
	def listuris( self ):
		return self._data['uris']

	def uri_id( self, uri ):
		#TODO: add search for uri
		for key, value in list.iteritems():
		    if value == url:
			return key
		return False

	def gettasks( self ):
		return self._data['tasks']

	def dotask( self, taskid ):
		return toolbox.do_tasksequence( self._data['tasks'][taskid], self._data, None )

	def load( self ):
		# TODO add documentation
		if( os.path.exists( self._filename ) ):
			tmp = pickle.load( open( self._filename, "rb" ) )
			self._data = tmp
			return tmp
		else:
			print "Couldn't find filename"
			return False

	def addtask( self, taskname, taskdef ):
		""" adds a new task to the stored tasks """
		if( taskname not in self.gettasks() ):
			self._data['tasks'][taskname] = taskdef

	def save( self ):
		""" saves the internal data for the class """
		pickle.dump( self._data, open( self._filename, "wb" ) )

if( __name__ == '__main__' ):
	lf = LookFor( None, "lookfordata.pickle" )
#	lf._data = lookfordata
#	lf.save()
#	taskdata = lf.dotask( 'eztv_Bones' )
	foundrows = []
	for task in lf.gettasks():
		taskdata = lf.dotask( task )
		#toolbox.do_tasksequence( task_sequence, { "url" : str( lookfor_uris[1]) }, None )
		if( taskdata['found'] ):
			foundrows += ( taskdata['data'] )
		else:
			print "task failed to find info"
	if len( foundrows ) > 0:
		print "Found something you were looking for!"
		htmlfile = "<html><Head></head><body><table>{}</table></body></html>".format( "\n".join( foundrows ) )
		toolbox.writefile( "data/test.html", htmlfile )


