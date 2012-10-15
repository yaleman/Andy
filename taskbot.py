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
		self.pluginname = "task"
		self._data = { 'uris' : {}, 'tasks' : {} }
		self._filename = config.filename[self.pluginname]
		# load the stored data
		self._load()

		#TODO move the compiled regexes to a dict
		self._basetask = { 'enabled' : False, 'period' : 0, 'lastdone' : 0 }
		self._re_tr = re.compile( "(<tr[^>]*>(.*?)</tr[^>]*>)" )
		self._re_table = re.compile( "(<table[^>]*>(.*?)</table[^>]*>)" )
		self._re_addstep_testinput = re.compile( "(?P<taskname>[\S]*) (?P<stepid>[0-9]*) (?P<details>[\S^\:]*:(.*))" )

		self._re_delstep_testinput = re.compile( "(?P<taskname>[\S]*) (?P<stepid>[0-9]*)" )
		self._taskswithfunctions = [ 'geturi', 'find_tr_with', 'find_table_with' 'strip_nl' ]


###############################
# 
# task steps
#
#


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

	def _task_find_tr_with( self, t, args, data ):
		needle = t[1]
		print "Looking for {}".format( needle )
		rows = self._re_tr.findall( data )
		if( len( rows ) > 0 ):
			found_rows = [ row[0] for row in rows if needle in row[0] ]
#			for row in [ row[0] for row in rows ]:
#				if( needle in row ):
#					found_rows.append( row )
			if( len( found_rows ) > 0 ):
				data = "\n".join( found_rows )
				print "Found {} matching rows".format( len( found_rows ) )
				args['found'] = True
			else:
				print "Found rows, but no matches."
				args['found'] = False
		else:
			print "Found no rows in data"
			args['found'] = False
		if args['found']:
			return args, data
		return False

	def _task_find_table_with( self, t, args, data ):
		needle = t[1]
		tables = self._re_table.findall( data )
		args['found'] = False
		if( len( tables ) > 0 ): # if found a table or two
			goodtables = [ table[0] for table in tables if needle in table[0] ] 
			data = "\n".join( goodtables )
			if( len( data ) > 0 ):
				args['found'] = True
				print "Found {} tables, {} had the needle.".format( len( tables ), len( goodtables ) )
				return args, data
			else:
				print "Found {} tables, 0 had the needle. ({})".format( len( tables ), needle )
				args['found'] == False
				return False
		else:
			print "Found no tables"
		return False

	def _task_replace( self, t, args, data ):
		search, replace = t[1].split( "|" )
		print "Replacing '{}' with '{}'".format( search, replace )
		data = data.replace( search, replace )
		return args, data
	
	def _task_replacewithspace( self, t, args, data ):
		data = data.replace( t[1].strip(), " " )
		return args, data

	def _task_dotask( self, t, args, data ):
		if( self._is_validtask( t[1] ) ):
			tmp = self.do	( t[1] )
			args = tmp
			data = tmp['data']
			return args, data
		else:
			return False

	def _task_in( self, t, args, data ):
		if( t[1] in data ):
			print "Found '{}' in data.".format( cmdargs ) 
			args['found'] = True
		else:
			print "Couldn't find '{}' in data.".format( cmdargs )
			args['found'] = False
		return args, data

	
###############################
# 
# main task processor 
#
	def do( self, taskid ):
		""" do an individual task """
		return self._do_tasksequence( taskid, self._data, None )

	def _do_tasksequence( self, taskname, args, data ):
		""" feed this a {} of tasks with the key as an int of the sequence, and it'll do them """
		if not self._is_validtask( taskname ):
			return "Invalid task '{}'".format( taskname )
		tasks = self._get_tasksteps( taskname )		
		print "tasks: {}".format( tasks )
		args['found'] = False
		# a task should be a taskname:stufftodo
		for step in tasks: 
			print "Task {}:".format( step ),
			t = self._data['tasks'][taskname][step].split( ":" )
			#t = task_sequence[ step ].split( ":" )
			cmd = t[0]
			cmdargs = t[1]
			# for a given task step, check if there's a self.function with the name _task_[step] and use that (all steps should be in these functions)
			if( "_task_{}".format( cmd ) in dir( self ) ): 
				tmp = eval( "self._task_{}( t, args, data )".format( cmd ) )
				if tmp != False:
					args, data = tmp
				else:
					return "Task {} stopped at step {}.".format( taskname, step )

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
		return "Task #{} added to {}, new definition:\n{}".format( stepid, newtask, self.showtask( newtask ) ) 

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
				#TODO check if still has steps and disable if none
				return "Successfully removed step #{} from {}.".format( stepid, taskname )
			return "Step #{} doesn't exist in task {}.".format( stepid, taskname )
		return "Invalid task '{}' requested.".format( taskname )

	def addtask( self, taskname ):
		""" adds a new task to the stored tasks """
		if( taskname not in self.gettasks() ):
			self._data['tasks'][taskname] = self._basetask
		return "added task"

	def deltask( self, taskname ):
		""" deletes a task """
		#TODO add some sort of verification?
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


