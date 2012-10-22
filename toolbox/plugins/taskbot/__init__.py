#!/usr/bin/env python

try:
	import pexpect
except ImportError:
	print( "Couldn't load pexpect" )

import re
import toolbox
import toolbox.steps
import config
import os
import time
import pickle

#TODO add a step to the eztv tasks that deal with the silly magnet links?

tasklet_idea = """
tasklet

uri:[hash] = uri (http://www.google.com)

data = download contnts from uri:[hash]


regex:[hash] = "(<?P=trtotal\<tr(?P=trinner.*)\>(?P=trcontents)</tr>)" etc
re.compile( regex:[hash] )
tr's = apply the regex to the data
"""

class Plugin( toolbox.base_plugin ):
	def __init__( self, parent ):
		toolbox.base_plugin.__init__( self, parent )
		self.pluginname = "task"
		self._data = { 'uris' : {}, 'tasks' : {} }
		self._filename = config.filename[self.pluginname]
		# load the stored data
		self._load()
		self._validsteps = self._buildvalidsteps()
		#TODO move the compiled regexes to a dict
		self._basetask = { 'enabled' : False, 'period' : 300, 'lastdone' : 0 }

		self._re_addstep_testinput = re.compile( "(?P<taskname>[\S]*) (?P<stepid>[0-9]*) (?P<details>[\S^\:]*:(.*))" )
		self._re_movestep_testinput = re.compile( "^(?P<taskname>[\S]+) (?P<oldstep>[\d]+) (?P<newstep>[\d]+).*" )
		self._re_delstep_testinput = re.compile( "(?P<taskname>[\S]*) (?P<stepid>[0-9]*)" )
		self._re_magnetfinder = re.compile( 'href="(magnet:\?[^\"]+)"' )


	def _buildvalidsteps( self ):
		#self._validsteps = [ step for step in dir( toolbox.steps ) if not step.startswith( "_" ) ]
		return self._validsteps
	
###############################
# 
# main task processor 
#
	def runall( self, text ):
		print( text )
		""" runs all the enabled tasks in taskbot """
		tasktorun = self._gettasks_enabled()
		print( "Tasks: {}".format( ",".join( tasktorun ) ) )
		for t in tasktorun:
			print( "Running: {}".format( t ) )
			self.do( t )
		return "Done."
			

	def do( self, taskid ):
		""" do an individual task """
		if( not self._is_validtask( taskid ) ):
			print(  "Invalid task requested in do( '{}' )".format( taskid ) )
			return False
		self._data['tasks'][taskid]['lastdone'] = time.time()
		self._parent._save_before_shutdown()
		tmp = self._do_tasksequence( taskid, self._data, None )
		if tmp != False:
			tmp, data = tmp
			return data
		else:
			return "Task failed"

	def run( self, taskid ):
		""" this is an alias of self.do """
		return self.do( taskid )

	def _do_tasksequence( self, taskname, args, data ):
		""" feed this a {} of tasks with the key as an int of the sequence, and it'll do them """
		taskobject = self._data['tasks'].get( taskname, None )
		if taskobject == None:
			print( "Invalid task '{}'".format( taskname ) )
			return False
		steps = self._get_tasksteps( taskobject )
		if len( steps ) == 0: 
			print( "Task has no steps." )
			return False
		# pull the task out as an object
		
		args['found'] = False
		# a task should be a taskname:stufftodo
		for step in steps:
			t = taskobject[step].split( ":" )
			# deal with steps that have : in their commands
			if( len( t ) > 2 ):
				t[1] = ":".join( t[1:] )
			cmd = t[0]
			if cmd in self._validsteps:
				# user-settable functions, go!
				tmp = getattr( toolbox.steps, cmd )( self, t, args, data )
				if tmp == False:
					print( "Task {} stopped at step {}.".format( taskname, step ) )
				# 	either return the false or the invalid data
					return tmp
				else:
					args, data = tmp	
			else:
				print( "Unknown task cmd '{}'".format( cmd ) )
		args['data'] = data
		if tmp != False:
			return args, data
		print( "_do_tasksequence stopped" )
		return False

	def geturis( self, text=None ):
		""" returns a list of all uri's """
		return self._data['uris']

	def _uri_id( self, uri ):
		""" returns the key for a given uri """
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
		""" sets the enable bit to False on a task """
		self._set_enable( taskid, False )
		return "Disabled {}".format( taskid )
	
	def enable( self, taskid ):
		""" sets the enable bit to True on a task """
		self._set_enable( taskid, True )
		return "Enabled {}".format( taskid )
	
	def show( self, taskid ):
		retval = ""
		if taskid == "":
				return ", ".join( self._data['tasks'].keys() )
		if taskid in self._data['tasks']:
			for displaytask in [ "{}\t{}".format( key, value ) for key, value in sorted( self._data['tasks'][taskid].items() ) ]:
				retval += "{}\n".format( displaytask )
			return retval 
		else:
			return "'{}' is not a valid task.".format( taskid )

###############################
# 
# private task listing steps
#
#
	def schedule( self, text=None ):
		goodtasks = "\n".join( sorted( [ "{}\t{}".format( self._timetorun( t ), t ) for t in self._gettasks_enabled() ] ) )
		disabledtasks = "\n".join( [ "never\t{}".format( t ) for t in self._gettasks_disabled() ] )
		return "secs\ttask\n{}\n{}".format( goodtasks, disabledtasks )
			
	def _timetorun( self, t=None):
		""" will return 0 if the task has no lastdone, or return the number of seconds until it's due to run 
			negative numbers show it's overdue """
		if( self._is_validtask( t.strip() ) ):
			taskobject = self._gettask( t )
			if( taskobject['lastdone'] == 0 ):
				return 0.0
			else:
				runtime = taskobject['lastdone'] + taskobject['period']
				#print( "Runtime for {}: {}".format( t, runtime ) )
				runtime = int( runtime - time.time() )
				return runtime
		return False

	def _gettasks_enabled( self, text=None ):
		return [ t for t in self._gettasks() if self._data['tasks'][t]['enabled'] == True ]

	def _gettasks_disabled( self, text=None ):
		return [ t for t in self._gettasks() if self._data['tasks'][t]['enabled'] == False ]

	def _gettask( self, taskname ):
		""" returns false if it's not a valid task """
		return self._data['tasks'].get( taskname, False )


	def _gettasks( self, text=None ):
		""" returns a list of all task-keys """
		return self._data['tasks'].keys()

	def _readytorun( self, taskname ):
		""" checks if a task is due to run """
		taskdata = self._gettask( taskname )
		if taskdata:
			runtime = taskdata['lastdone'] + taskdata['period']
			if time.time() > runtime:
				return True
		return False

###############################
# 
# manipulating task steps
#
#


	def movestep( self, text ):

		s = self._re_movestep_testinput.match( text )
		if( s != None ):
			taskname = s.group( 'taskname' )
			oldstep = int( s.group( 'oldstep' ) )
			newstep = int( s.group( 'newstep' ) )
			force = False
			if( text.lower().endswith( 'force' ) ):
				force = True
			if( self._is_validtask( taskname ) ):
				taskobject = self._data['tasks'][taskname]
				if( taskobject.get( oldstep, None ) != None ):
					if( taskobject.get( newstep, None ) == None or force == True ):

						taskobject[newstep] = taskobject.get( oldstep )
						del( taskobject[oldstep] )
						return "Movestep valid, moving task {} step #{} to #{}".format( taskname, oldstep, newstep )
					return "Can't overwrite steps without force"
				return "Can't move steps, oldstep doesn't exist"
			return "Invalid task specified"
		return "Movestep usage: movestep [taskname] [oldstep] [newstep] [force(optional)]"

	def addstep( self, text ):
		# check it's a valid task definition
		s = self._re_addstep_testinput.match( text )
		if( s != None ):
			#print "Details definition valid"
			pass
		else:
			return "Invalid task definition supplied, should be 'addstep [taskname] [stepid] [details]'"
		newtask = s.group( 'taskname' )
		stepid = int( s.group( 'stepid' ) )
		details = s.group( 'details' )
		# check if the task exists
		print( "Task: '{}'... ".format( newtask ) ),
		if( self._is_validtask( newtask ) ):
			print( "[OK]" )
		else:
			print( "[ERR]" )
			return "Invalid task specified, please try one of these: {}".format( ", ".join( self._gettasks() ) )
		# check if the step's already there, don't want to overwrite
		if( self._data['tasks'][newtask].get( stepid, None ) != None ):
			return "Step already set, stopping"
		try:
			self._data['tasks'][newtask][stepid] = details
		except KeyError:
			return "Something broke with self._data['tasks'][newtask][stepid] = details"
		return "Task #{} added to {}".format( stepid, newtask ) 

	def delstep( self, text ):
		""" removes a step from a task, delstep [taskname] [stepid] """
		s = self._re_delstep_testinput.match( text )
		if( s != None ):
			pass
		else:
			return "Invalid delstep request, should be 'delstep [taskname] [stepid]'"
		taskname = s.group( 'taskname' )
		# check if it's a valid task
		if( self._is_validtask( taskname ) ):	
			stepid = int( s.group( 'stepid' ) )
			# check if the step is valid
			if( stepid in self._data['tasks'][taskname] ):
				del( self._data['tasks'][taskname][stepid] )
				if not self._task_hassteps( taskname ):
					self.disable( taskname )
				return "Successfully removed step #{} from {}.".format( stepid, taskname )
			return "Step #{} doesn't exist in task {}.".format( stepid, taskname )
		return "Invalid task '{}' requested.".format( taskname )

	def add( self, taskname ):
		""" adds a new task to the stored tasks """
		if( taskname not in self._gettasks() ):
			self._data['tasks'][taskname] = self._basetask
		return "added task"

	def delete( self, taskname ):
		""" deletes a task """
		if( taskname in self._gettasks() ):
			del( self._data['tasks'][taskname] )
		return "removed task '{}'".format( taskname )

###############################
# 
# checks and balances
#
#

	def _is_validtaskobject( self, taskobject ):	
		if taskobject in self._data['tasks'].items():
			return True
		return False

	def _is_validtask( self, tasktocheck ):
		""" should return True if a task by that name exists """
		if( tasktocheck in self._data['tasks'] ):
			return True
		return False

	def _task_hassteps( self, taskobject ):
		""" will return true if the task has valid steps, false if not """
		if( len( self._get_tasksteps( taskobject ) ) > 0 ):
			return True
		return False

	def _get_tasksteps( self, taskobject ):
		ret_steps = sorted( [ key for key in taskobject if isinstance( key, int ) ] )
		#print ret_steps
		return ret_steps

#
#if( __name__ == '__main__' ):
#	lf = Plugin( None, "lookfordata.pickle" )
#
#	foundrows = []
#	for task in lf._gettasks():
#	lf._save()
#	if len( foundrows ) > 0:
#		print( "Found something you were looking for!" )
#		htmlfile = "<html><Head></head><body><table>{}</table></body></html>".format( "\n".join( foundrows ) )
#		toolbox.writefile( "data/test.html", htmlfile )
#

