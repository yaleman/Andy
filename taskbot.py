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

class taskbot( toolbox.base_plugin ):
	def __init__( self, parent ):
		toolbox.base_plugin.__init__( self, parent )
		self.pluginname = "taskbot"
		self._data = { 'uris' : {}, 'tasks' : {} }
		self._filename = config.filename[self.pluginname]
		# load the stored data
		self._load()

		# hack for when I messed up a key - JH 2012-10-14
		for t in self._data['tasks']:
			if( self._data['tasks'][t].get( 'enable', None ) != None ):
				del( self._data['tasks'][t]['enable'] )

		self._basetask = { 'enabled' : False, 'period' : 0, 'lastdone' : 0 }
		self._re_tr = re.compile( "(<tr[^>]*>(.*?)</tr[^>]*>)" )
		self._re_table = re.compile( "(<table[^>]*>(.*?)</table[^>]*>)" )

		self._taskswithfunctions = [ 'geturi', 'find_tr_with', 'find_table_with' 'strip_nl' ]


###############################
# 
# task steps
#
#


	def _task_geturi( self, t, args, data ):
		uri = args[ 'uris' ][ int( t[1] ) ]
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
		found_rows = []
		if( len( rows ) > 0 ):
			for row in [ row[0] for row in rows ]:
				if( needle in row ):
					found_rows.append( row )
			if( len( found_rows ) > 0 ):
				data = found_rows
				print "Found {} matching rows".format( len( found_rows ) )
				args['found'] = True
			else:
				print "Found rows, but no matches."
				args['found'] = False
		else:
			print "Found no rows in data"
			args['found'] = False
		return args, data

	def _task_find_table_with( self, t, args, data ):
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
		return args, data

###############################
# 
# main task processor 
#
	def dotask( self, taskid ):
		""" do an individual task """
		return self._do_tasksequence( self._data['tasks'][taskid], self._data, None )

	def _do_tasksequence( self, task_sequence, args, data ):
		""" feed this a {} of tasks with the key as an int of the sequence, and it'll do them """
		tasks = sorted( [ key for key in task_sequence.iterkeys() if isinstance( key, int ) ] )		
		print "tasks: {}".format( tasks )
		args['found'] = False
		# a task should be a taskname:stufftodo
		for step in tasks: 
			print "Task {}:".format( step),
			t = task_sequence[ step ].split( ":" )
			cmd = t[0]
			cmdargs = t[1]
			# for a given task step, check if there's a self.function with the name _task_[step] and use that (all steps should be in these functions)
			if( "_task_{}".format( cmd ) in dir( self ) ): 
				args, data = eval( "self._task_{}( t, args, data )".format( cmd ) )

			elif( cmd == "replace" ):
				search, replace = t[1].split( "|" )
				print "Replacing '{}' with '{}'".format( search, replace )
				data = data.replace( search, replace )
				#print data

			elif( cmd == "email" ):
				#TODO add email functionality to do_tasksequence
				print "This functionality is not added yet."

			elif( cmd == "writefile" ):
				#TODO add file writing functionality to do_tasksequence
				print "This functionality is not added yet."

			elif( cmd == "tweet" ):
				#TODO add tweet functionality
				print "Can't tweet yet"

			#TODO add some way of going "if found, do the next step"

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

	def listuris( self, text=None ):
		return self._data['uris']

	def _uri_id( self, uri ):
		for key, value in self._data['uris'].iteritems():
			if value == uri:
				return key
		return False

###############################
# 
# setting task flags 
#
#

	def _set_enable( self, taskid, value = True ):
		if( self._is_validtask( taskid ) ):
			self._data['tasks'][taskid]['enabled'] = value

	def disable( self, taskid ):
		self._set_enable( taskid, False )
		return "Disabled {}".format( taskid )
	
	def enable( self, taskid ):
		self._set_enable( taskid, True )
		return "Enabled {}".format( taskid )


	def gettasks( self, text=None ):
		return self._data['tasks'].keys()

	def showtask( self, taskid ):
		retval = ""
		if taskid in self._data['tasks']:
			for displaytask in [ "{}\t{}".format( key, value ) for key, value in sorted( self._data['tasks'][taskid].items() ) ]:
				retval += "{}\n".format( displaytask )
			return retval 
		else:
			return "'{}' is not a valid task.".format( taskid )


	def addstep( self, text ):
		print "Was handed '{}'".format( text )
		re_addstep_testinput = re.compile( "(?P<taskname>[\S]*) (?P<stepid>[0-9]*) (?P<details>[a-z]*:[\s\S]{0,})" )
		# check it's a valid task definition
		s = re_addstep_testinput.match( text )
		if( s != None ):
			print "Details definition valid"
		else:
			return "Invalid task definition supplied, should be '[taskname] [stepid] [details]'"
		newtask = s.group( 'taskname' )
		stepid = int( s.group( 'stepid' ) )
		details = s.group( 'details' )
		# check if the task exists
		print "Task: '{}'... ".format( newtask ),
		if( self._is_validtask( newtask ) ):
			print "[OK]"
		else:
			print "[ERR]"
			return "Invalid task specified, please try one of these: {}".format( ", ".join( self.gettasks() ) )
		# check if the step's already there, don't want to overwrite
		if( self._data['tasks'][newtask].get( stepid, None ) != None ):
			return "Step already set, stopping"
		print "Step number: {}".format( stepid )
		print "Step definition: '{}'".format( details )
		try:
			self._data['tasks'][newtask][stepid] = details
		except KeyError:
			return "Fucked it."
		return "Task #{} added to {}, new definition:\n{}".format( stepid, newtask, self.showtask( newtask ) ) 

	def addtask( self, taskname ):
		""" adds a new task to the stored tasks """
		if( taskname not in self.gettasks() ):
			self._data['tasks'][taskname] = self._basetask
		return "added task"

###############################
# 
# checks and balances
#
#

	def _is_validtask( self, tasktocheck ):
		""" should return True if a task by that name exists """
		if( tasktocheck in self._data['tasks'] ):
			return True
		return False





if( __name__ == '__main__' ):
	lf = taskbot( None, "lookfordata.pickle" )
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
	lf._save()
	if len( foundrows ) > 0:
		print "Found something you were looking for!"
		htmlfile = "<html><Head></head><body><table>{}</table></body></html>".format( "\n".join( foundrows ) )
		toolbox.writefile( "data/test.html", htmlfile )


