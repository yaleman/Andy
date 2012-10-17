#!/usr/bin/env python

try:
	import pexpect
except ImportError:
	print "Couldn't load pexpect"
import re
import toolbox
import config
import os
import time
import pickle


def dotask( self, t, args, data ):
	""" does another task """
	print "Doing subtask: {}".format( t[1] )
	return self._do_tasksequence( t[1], args, data )

def stripnl( taskbot, t, args, data ):
	return args, data.replace( "\n", " " )

def striptab( taskbot, t, args, data ):
	return args, data.replace( "\t", " " )

def email( self, t, args, data ):
	#TODO add email functionality to do_tasksequence
	print "Email functionality is not added yet, failing just in case."
	return False

def tweet( self, t, args, data ):
	#TODO add tweeting function to taskbot
	print "Tweet functionality is not added yet, failing just in case."
	return False


def findhref_magnet( self, t, args, data ):
	
	s = self._re_magnetfinder.findall( data )
	if s != None:
		return args, "\n".join( s )

def retstring( self, text ):
	print "retstring not implemented yet, failing"
	return False


def geturi( self, t, args, data ):
	uri = args[ 'uris' ][ int( t[1] ) ]
	print "Grabbing uri: {}".format( uri ),
	# pulls the file from the filecache if possible, caches for config.uricachetime seconds
	data = self._parent.plugins['filecache'].getfile( uri, config.uricachetime )
	print "[OK] Filesize: {}".format( len( data ) )
	return args, data


# TODO refactor __task_find_tag_with and __task_find_tag_without to make them one function that just takes an option NESTING WOO
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
			data = "\n".join( found_tags )
			args['found'] = True
		else:
			print "Found {} but no matches.".format( tag )
			return False
	else:
		print "Found no {} in data.".format( tag )
	if args['found']:
		return args, data
	print "No tag {} found in data.".format( tag )
	return False

def __task_find_tag_without( self, tag, t, args, data ):
	""" searches data for html tags and returns the tags without needle (or t[1]) in them """
	needle = t[1]
	print "Looking for '{}' in tag {}".format( needle, tag )
	tagre = "(<{}[^>]*>(.*?)</{}[^>]*>)".format( tag, tag )
	tagfinder = re.compile( tagre )
	tagpairs = tagfinder.findall( data )
	if( len( tagpairs ) > 0 ):
		found_without_tags = [ x[0] for x in tagpairs if needle not in x[0] ]
		if( len( found_without_tags ) > 0 ):
			print "Found {} matching {}.".format( len( found_without_tags ), tag )
			data = "\n".join( found_without_tags )
			args['found'] = True
		else:
			print "Found {} but no valid matches.".format( tag )
			return False
	else:
		print "Found no valid {} in data.".format( tag )
	if args['found']:
		return args, data
	return False

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
	print "Writing to {}".format( t[1] )
	f = open( t[1], 'w' )
	f.write( data )
	f.close
	return args, data

def setperiod( self, t, args, data ):
	""" this should be able to set the period on a task out to x time if it's triggered, useful for things like periodic checkers 
	that can delay themselves for normaltime x 3 on success or similar, then reset it back next time """
	#TODO finish taskbox._task_selfdelay
	tmp = t[1].split( "|" )
	if( len( tmp ) == 2 ):
		target, newperiod = tmp
	else:
		return False
	return args, data

