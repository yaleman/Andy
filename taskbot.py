#!/usr/bin/env python

try:
	import pexpect
except ImportError:
	print "Couldn't load pexpect"
import re
import toolbox
import config
import os
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

class taskbot( toolbox.base_plugin ):
	def __init__( self, parent ):
		toolbox.base_plugin.__init__( self, parent )
		self.pluginname = "task"
		self._data = { 'uris' : {}, 'tasks' : {} }
		self._filename = config.filename[self.pluginname]
		# load the stored data
		self._load()

		#TODO move the compiled regexes to a dict
		self._basetask = { 'enabled' : False, 'period' : 0, 'lastdone' : 0 }
		self._re_addstep_testinput = re.compile( "(?P<taskname>[\S]*) (?P<stepid>[0-9]*) (?P<details>[\S^\:]*:(.*))" )

		self._re_delstep_testinput = re.compile( "(?P<taskname>[\S]*) (?P<stepid>[0-9]*)" )


	
###############################
# 
# main task processor 
#
	def runall( self, text ):
		""" runs all the enabled tasks in taskbot """
		for t in self._gettasks_enabled():
			print "Running: {}".format( t )
			self.do( t )
		return "Done."
			

	def do( self, taskid ):
		""" do an individual task """
		if( not self._is_validtask( taskid ) ):
			return "Invalid task requested in do( '{}' )".format( taskid )
		return self._do_tasksequence( taskid, self._data, None )

	def _do_tasksequence( self, taskname, args, data ):
		""" feed this a {} of tasks with the key as an int of the sequence, and it'll do them """
		if not self._is_validtask( taskname ):
			return "Invalid task '{}'".format( taskname )
		tasks = self._get_tasksteps( taskname )		
		args['found'] = False
		# a task should be a taskname:stufftodo
		for step in tasks: 
			t = self._data['tasks'][taskname][step].split( ":" )
			# deal with steps that have : in their commands
			if( len( t ) > 2 ):
				t[1] = ":".join( t[1:] )
			cmd = t[0]
			# for a given task step, check if there's a self.function with the name _task_[step] and use that (all steps should be in these functions)
			if( "_task_{}".format( cmd ) in dir( self ) ): 
				tmp = eval( "self._task_{}( t, args, data )".format( cmd ) )
				if tmp == False:
					return "Task {} stopped at step {}.".format( taskname, step )
				else:
					args, data = tmp
					
			else:
				print "Unknown task cmd '{}'".format( cmd )
		args['data'] = data
		return args

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
		self._set_enable( taskid, False )
		return "Disabled {}".format( taskid )
	
	def enable( self, taskid ):
		self._set_enable( taskid, True )
		return "Enabled {}".format( taskid )


	def list( self, text=None):
		return ", ".join( self._data['tasks'].keys() )

	def _gettasks_enabled( self, text=None ):
		return [ t for t in self.gettasks() if self._data['tasks'][t]['enabled'] == True ]

	def _gettasks_disabled( self, text=None ):
		return [ t for t in self.gettasks() if self._data['tasks'][t]['enabled'] == False ]


	def gettasks( self, text=None ):
		return self._data['tasks'].keys()

	def show( self, taskid ):
		retval = ""
		if taskid in self._data['tasks']:
			for displaytask in [ "{}\t{}".format( key, value ) for key, value in sorted( self._data['tasks'][taskid].items() ) ]:
				retval += "{}\n".format( displaytask )
			return retval 
		else:
			return "'{}' is not a valid task.".format( taskid )
###############################
# 
# manipulating task steps
#
#


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
		print "Task: '{}'... ".format( newtask ),
		if( self._is_validtask( newtask ) ):
			pass
			#print "[OK]"
		else:
			print "[ERR]"
			return "Invalid task specified, please try one of these: {}".format( ", ".join( self.gettasks() ) )
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

	def addtask( self, taskname ):
		""" adds a new task to the stored tasks """
		if( taskname not in self.gettasks() ):
			self._data['tasks'][taskname] = self._basetask
		return "added task"

	def delete( self, taskname ):
		""" deletes a task """
		if( taskname in self.gettasks() ):
			del( self._data['tasks'][taskname] )
		return "removed task '{}'".format( taskname )

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

	def _task_hassteps( self, tasktocheck ):
		""" will return true if the task has valid steps, false if not """
		if( self._is_validtask( tasktocheck ) ):
			if( len( self._get_tasksteps( tasktocheck ) ) > 0 ):
				return True
		return False

	def _get_tasksteps( self, taskname ):
		if( self._is_validtask( taskname ) ):
			return sorted( [ key for key in self._data['tasks'][taskname].iterkeys() if isinstance( key, int ) ] )

###############################
# 
# task steps
#
#
	def _task_email( self, t, args, data ):
		#TODO add email functionality to do_tasksequence
		print "Email functionality is not added yet, failing just in case."
		return False

	def _task_tweet( self, t, args, data ):
		#TODO add tweeting function to taskbot
		print "Tweet functionality is not added yet, failing just in case."
		return False

	def _task_geturi( self, t, args, data ):
		uri = args[ 'uris' ][ int( t[1] ) ]
		print "Grabbing uri: {}".format( uri )
		# pulls the file from the filecache if possible, caches for config.uricachetime seconds
		data = self._parent.plugins['filecache'].getfile( uri, config.uricachetime )
		return args, data

	def _task_stripnl( self, t, args, data ):
		return args, data.replace( "\n", " " )

	def _task_striptab( self, t, args, data ):
		return args, data.replace( "\t", " " )

	def __task_find_tag_with( self, tag, t, args, data ):
		""" searches data for html tags with needle (or t[1]) inside them """
		needle = t[1]
		print "Looking for '{}' in tag {}".format( needle, tag )
		tagre = "(<{}[^>]*>(.*?)</{}[^>]*>)".format( tag, tag )
		tagfinder = re.compile( tagre )
		tagpairs = tagfinder.findall( data )
		if( len( tagpairs ) > 0 ):
			found_tags = [ x[0] for x in tagpairs if needle in x[0] ]
			if( len( found_tags ) > 0 ):
				print "Found {} matching {}.".format( len( found_tags ), tag )
				args['found'] = True
			else:
				print "Found {} but no matches.".format( tag )
				return False
		else:
			print "Found no {} in data.".format( tag )
		if args['found']:
			return args, data
		return False
	
	def _task_find_td_with( self, t, args, data ):
		""" see __task_find_tag_with, searches for td's """
		return self.__task_find_tag_with( "td", t, args, data )

	def _task_find_tr_with( self, t, args, data ):
		""" see __task_find_tag_with, searches for tr's """
		return self.__task_find_tag_with( "tr", t, args, data )

	def _task_find_table_with( self, t, args, data ):
		""" see __task_find_tag_with, searches for tables """
		return self.__task_find_tag_with( "table", t, args, data )


	def _task_replace( self, t, args, data ):
		""" replaces whatever's between the : and the | with whatever's after the | """
		search, replace = t[1].split( "|" )
		data = data.replace( search, replace )
		return args, data
	
	def _task_replacewithspace( self, t, args, data ):
		""" replaces the input data with spaces """
		data = data.replace( t[1].strip(), " " )
		return args, data

	def _task_dotask( self, t, args, data ):
		""" does another task """
		if( self._is_validtask( t[1] ) ):
			print "Doing subtask: {}".format( t[1] )
			tmp = self.do( t[1] )
			args = tmp
			data = tmp['data']
			return args, data
		else:
			return False

	def _task_in( self, t, args, data ):
		""" check if something's in the input data """
		if( t[1] in data ):
			#print "Found '{}' in data.".format( cmdargs ) 
			args['found'] = True
			return args, data
		else:
			#print "Couldn't find '{}' in data.".format( cmdargs )
			args['found'] = False
			return False

	def _task_writefile( self, t, args, data ):
		print "Writing to {}".format( t[1] )
		f = open( t[1], 'w' )
		f.write( data )
		f.close
		return args, data

	def _task_setperiod( self, t, args, data ):
		""" this should be able to set the period on a task out to x time if it's triggered, useful for things like periodic checkers 
		that can delay themselves for normaltime x 3 on success or similar, then reset it back next time """
		#TODO finish taskbox._task_selfdelay
		tmp = t[1].split( "|" )
		if( len( tmp ) == 2 ):
			target, newperiod = tmp
		else:
			return False
		return args, data

if( __name__ == '__main__' ):
	lf = taskbot( None, "lookfordata.pickle" )

	foundrows = []
	for task in lf.gettasks():
		lf.do( task )
	lf._save()
	if len( foundrows ) > 0:
		print "Found something you were looking for!"
		htmlfile = "<html><Head></head><body><table>{}</table></body></html>".format( "\n".join( foundrows ) )
		toolbox.writefile( "data/test.html", htmlfile )


