#!/usr/bin/env python

try:
	import pexpect
except ImportError:
	print "Couldn't load pexpect"
import re
import toolbox
import config
import os, pickle

#TODO add a step to the eztv tasks that deal with the silly magnet links?

tasklet_idea = """
tasklet

uri:[hash] = uri (http://www.google.com)

data = download contnts from uri:[hash]


regex:[hash] = "(<?P=trtotal\<tr(?P=trinner.*)\>(?P=trcontents)</tr>)" etc
re.compile( regex:[hash] )
tr's = apply the regex to the data
"""

class TaskBot( config.base_plugin ):
	def __init__( self, parent, filename, config=config ):
		config.base_plugin.__init__( self, parent )
		self._config = config
		self.pluginname = "taskbot"
		self._data = { 'uris' : {}, 'tasks' : {} }
		self._filename = filename
		self.load()
		self._re_tr = re.compile( "(<tr[^>]*>(.*?)</tr[^>]*>)" )
		self._re_table = re.compile( "(<table[^>]*>(.*?)</table[^>]*>)" )


	def _task_geturi( self, t, args, data ):
		uri = args[ 'uris' ][int( t[1] )]
		print "Grabbing uri: {}".format( uri )
		data = toolbox.url_get( uri )
		#data = open( 'data/page.cache', 'r' ).read()
		return args, data

	def _task_strip_nl( self, t, args, data ):
		return args, data.replace( "\n", " " )

	def _task_find_tr_with( self, t, args, data ):
		needle = t[1]
		print "Looking for {}".format( needle )
		rows = self._re_tr.findall( data )
		foundrows = []
		if( len( rows ) > 0 ):
			for row in [ row[0] for row in rows ]:
				if( needle in row ):
					foundrows.append( row )
			if( len( foundrows ) > 0 ):
				data = foundrows
				print "Found {} matching rows".format( len( foundrows ) )
				args['found'] = True
			else:
				print "Found rows, but no matches."
				args['found'] = False
		else:
			print "Found no rows in data"
			args['found'] = False
		return args, data

	def do_tasksequence( self, task_sequence, args, data ):
		# feed this a {} of tasks with the key as an int of the sequence, and it'll do them
		tasks = sorted( [ key for key in task_sequence.iterkeys() if isinstance( key, int ) ] )		
		print "tasks: {}".format( tasks )
		args['found'] = False
#		for key in task_sequence.iterkeys():
#			print type( key )
		for task in tasks: 
			print "Task {}:".format( task ),
			t = task_sequence[ task ].split( ":" )
			#print "'{}'".format( t )
			cmd = t[0]
			cmdargs = t[1]
			if( cmd == "geturi" ):
				args, data = self._task_geturi( t, args, data )
		
			elif( cmd == "find_tr_with" ):
				args, data = self._task_find_tr_with( t, args, data )
			elif( cmd == "strip_nl" ):
				args, data = self._task_strip_nl( t, args, data )

			elif( cmd == "replace" ):
				search, replace = t[1].split( "|" )
				print "Replacing '{}' with '{}'".format( search, replace )
				data = data.replace( search, replace )
				#print data

	
			elif( cmd == "find_table_with" ):
				needle = t[1]
				
				tables = self._re_table.findall( data )
				print "Found {} tables".format( len( tables ) )
				#print tables
				if( len( tables ) > 0 ): # if found a table or two
					for table in [ table[0] for table in tables ]:
						if( needle in table ):
							data = table
							print "\t Found a table with {} in it".format( needle )
							args['found'] = True
							break
						else:
							# table didn't match search
							pass
				args['found'] = False
		
			elif( cmd == "email" ):
				#TODO add email functionality to do_tasksequence
				print "This functionality is not added yet."

			elif( cmd == "writefile" ):
				#TODO add file writing functionality to do_tasksequence
				print "This functionality is not added yet."

			elif( cmd == "in" ):
				if( cmdargs in data ):
					print "Found '{}' in data.".format( cmdargs ) 
					args['found'] = True
				else:
					print "Couldn't find '{}' in data.".format( cmdargs )
					args['found'] = False
			else:
				print "Unknown task cmd '{}'".format( cmd )
		args['data'] = data
		return args

	def listuris( self ):
		return self._data['uris']

	def uri_id( self, uri ):
		for key, value in self._data['uris'].iteritems():
			if value == uri:
				return key
		return False

	def gettasks( self, text ):
		return self._data['tasks'].keys()


	def showtask( self, taskid ):
		retval = ""
		for task in [ "{}\t{}".format( key, value ) for key, value in sorted( self._data['tasks'][taskid].items() ) ]:
			retval += "{}\n".format( task )
		return retval 

	def dotask( self, taskid ):
		return self.do_tasksequence( self._data['tasks'][taskid], self._data, None )

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
		return "added task"

	def save( self ):
		""" saves the internal data for the class """
		pickle.dump( self._data, open( self._filename, "wb" ) )

if( __name__ == '__main__' ):
	lf = TaskBot( None, "lookfordata.pickle" )
#	lf._data = lookfordata
#	lf.save()
	#taskdata = lf.dotask( 'eztv_Bones' )
	foundrows = []
	for task in lf.gettasks():
		print lf.showtask( task )
		if( 'enabled' not in lf._data['tasks'][task] ):
			lf._data['tasks'][task]['enabled'] = True
		if( 'period' not in lf._data['tasks'][task] ):
			lf._data['tasks'][task]['period'] = 60 * 60 * 2
		if( 'lastdone' not in lf._data['tasks'][task] ):
			lf._data['tasks'][task]['lastdone'] = 0
#		taskdata = lf.dotask( task )
#		if( taskdata['found'] ):
#			foundrows += ( taskdata['data'] )
#		else:
#			print "task failed to find info"
	lf.save()
	if len( foundrows ) > 0:
		print "Found something you were looking for!"
		htmlfile = "<html><Head></head><body><table>{}</table></body></html>".format( "\n".join( foundrows ) )
		toolbox.writefile( "data/test.html", htmlfile )


