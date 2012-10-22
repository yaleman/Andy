#!/usr/bin/env python

try:
	import pexpect
except ImportError:
	print( "Couldn't load pexpect" )
import re
import toolbox
import config
import os
import time
import pickle

def join( self, t, args, data ):
	""" can do the join function on the data """
	if( t[1] == "newline" ):
		joiner = "\n"
	else:
		joiner = " "	

	if( type( data ) == "list" ):
		data = joiner.join( data )
	elif( type(data ) == "str" ):
		pass
	elif( type( data ) == "dict" ):
		data = joiner.join( [ "{} : {}".format( k, v ) for k, v in data.iteritems() ] )
	return args, data
	
def _preorappend( preorap, self, t, args, data ):
	""" prepends or appends something to the data, will convert things to strings if it can  """
	if( type( data ) != "str" ):
		args, data = join( self, t, args, data )
	if( len (t) > 2):
		t[1] = t[1:]

	if( preorap == 'ap' ):
		return args, data+t[1]
	elif( preorap == 'pre' ):
		return args, data+t[1]
	
def prepend( self, t, args, data ):
	return _preorappend( 'pre', self, t, args, data)

def append( self, t, args, data ):
	return _preorappend( 'ap', self, t, args, data )

def dotask( self, t, args, data ):
	""" does another task """
	print( "Doing subtask: {}".format( t[1] ) )
	return self._do_tasksequence( t[1], args, data )

def stripnl( taskbot, t, args, data ):
	return args, data.replace( "\n", " " )

def striptab( taskbot, t, args, data ):
	return args, data.replace( "\t", " " )

def email( self, t, args, data ):
	#TODO add email functionality to do_tasksequence
	print( "Email functionality is not added yet, failing just in case." )
	return False

def tweet( self, t, args, data ):
	#TODO add tweeting function to taskbot
	print( "Tweet functionality is not added yet, failing just in case." )
	return False


def findhref_magnet( self, t, args, data ):
	
	s = self._re_magnetfinder.findall( data )
	if s != None:
		return args, "\n".join( s )

def retstring( self, text ):
	print( "retstring not implemented yet, failing" )
	return False


def geturi( self, t, args, data ):
	uri = args[ 'uris' ][ int( t[1] ) ]
	print( "Grabbing uri: {}".format( uri ) ),
	# pulls the file from the filecache if possible, caches for config.filecache['uricachetime'] seconds
	data = self._parent.plugins['filecache'].getfile( uri, config.filecache['uricachetime'] )
	print( "[OK] Filesize: {}".format( len( data ) ) )
	return args, data


def __task_find_tag_filter( self, tag, t, args, data, yesorno ):
	""" searches data for html tags with needle (or t[1]) them if yesorno = True, or without them if yesorno = False """
	needle = t[1]
	print("Looking for '{}' in tag {}".format( needle, tag ) )
	tagre = "(<{}[^>]*>(.*?)</{}[^>]*>)".format( tag, tag )
	tagfinder = re.compile( tagre )

	# if it's  a list, retucn a merged list of results out of the list's items
	if type( data ) == "list":
		tagpairs = [ tagfinder.findall( d ) for d	 in data ]
		tagpairs = reduce( lambda x, y: x + y, tagpairs )
	# not really sure I want to deal with dicts?
	elif type( data ) == "dict":
		print( "Seriously, a dict in data?" )
		return False
	# strings are easy to deal with
	else:
		tagpairs = tagfinder.findall( data )

	if( len( tagpairs ) > 0 ):
		found_tags = [ x[0] for x in tagpairs if (needle in x[0]) == yesorno ]
		if( len( found_tags ) > 0 ):
			print( "Found {} matching {}.".format( len( found_tags ), tag ) )
			data = "\n".join( found_tags )
			args['found'] = True
		else:
			print( "Found {} but no matches.".format( tag ) )
			return False
	else:
		print( "Found no {} in data.".format( tag ) )
	if args['found']:
		return args, data
	print( "No tag {} found in data.".format( tag ) )
	return False


def __task_find_tag_with( self, tag, t, args, data ):
	""" searches data for html tags with needle (or t[1]) inside them """
	return __task_find_tag_filter( self, tag, t, args, data, True )

def __task_find_tag_without( self, tag, t, args, data ):
	""" searches data for html tags and returns the tags without needle (or t[1]) in them """
	return __task_find_tag_filter( self, tag, t, args, data, False )

def find_td_without( self, t, args, data ):
	""" see __task_find_tag_with, searches for td's """
	return __task_find_tag_without( self, "td", t, args, data )

def find_tr_without( self, t, args, data ):
	""" see __task_find_tag_with, searches for tr's """
	return __task_find_tag_without( self, "tr", t, args, data )

def find_table_without( self, t, args, data ):
	""" see __task_find_tag_with, searches for tables """
	return __task_find_tag_without( self, "table", t, args, data )

def find_td_with( self, t, args, data ):
	""" see __task_find_tag_with, searches for td's """
	return __task_find_tag_with( self, "td", t, args, data )

def find_tr_with( self, t, args, data ):
	""" see __task_find_tag_with, searches for tr's """
	return __task_find_tag_with( self, "tr", t, args, data )

def find_table_with( self, t, args, data ):
	""" see __task_find_tag_with, searches for tables """
	return __task_find_tag_with( self, "table", t, args, data )


def replace( self, t, args, data ):
	""" replaces whatever's between the : and the | with whatever's after the | """
	search, replace = t[1].split( "|" )
	data = data.replace( search, replace )
	return args, data

def replacewithspace( self, t, args, data ):
	""" replaces the input data with spaces """
	data = data.replace( t[1].strip(), " " )
	return args, data

def isin( self, t, args, data ):
	""" check if something's in the input data """
	if( t[1] in data ):
		#print "Found '{}' in data.".format( cmdargs ) 
		args['found'] = True
		return args, data
	else:
		#print "Couldn't find '{}' in data.".format( cmdargs )
		args['found'] = False
		return False

def writefile( self, t, args, data ):
	""" write the contents of data to the filename in t[1] """
	print( "Writing to {}".format( t[1] ) )
	f = open( t[1], 'w' )
	f.write( data )
	f.close
	return args, data

def setperiod( self, t, args, data ):
	""" this should be able to set the period on a task out to x time if it's triggered, useful for things like periodic checkers 
	that can delay themselves for normaltime x 3 on success or similar, then reset it back next time """
	tmp = t[1].split( "|" )
	#TODO should probably check if the target's valid in setperiod
	if( len( tmp ) == 2 ):
		target, newperiod = tmp
		self._data['tasks'][target]['period'] = int( newperiod )
	else:
		return False
	return args, data

