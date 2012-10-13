#!/usr/bin/env python

try:
	import pexpect
except ImportError:
	print "Failed to import pexpect"

#import subprocess
import pickle
import re, hashlib
import urllib2

def sudorun( command, password ):
	# uses pexpect to run a command with sudo on the command line with a given password and return the results. 
	# relies on pexpect
	child = pexpect.spawn ( "sudo {}".format( command ) )
	i = child.expect( [ 'Password:*', '' ] )
	lines = []
	if i == 0:
		child.sendline( password )
	else:
		lines.append( child.before.strip() )
	while not child.eof() :
		lines.append( child.readline().strip() )
	return lines


def run( command ):
	child = pexpect.spawn ( command )
	lines = []
	while not child.eof() :
		lines.append( child.readline().strip() )
	return lines

def self_ipaddr():
	# finds a list of the local ip addresses
	# relies on subprocess
	# only works on POSIX systems		
	ifconfig = run( "ifconfig" )
	re_ipfind = re.compile( "inet[6\s]{1,2}([a-f0-9\.\:]{3,})" )
	ipaddr = []
	for line in ifconfig:
		if "inet" in line and re_ipfind.search( line ) != None:
			ipaddr.append( re_ipfind.findall( line )[0] )
	return ipaddr

def url_get( url ):
	#based on info from here: http://docs.python.org/library/urllib2.html#urllib2.urlopen
	# create the request object
	#TODO deal with exceptions
	u = urllib2.urlopen( url )
	# u.geturl() should return whatever ended up being grabbed (In case of a redirect)
	return u.read()

def md5( text ):
	h = hashlib.new( 'ripemd160' )
	h.update( text )
	return h.hexdigest()

def writefile( filename, contents ):
	print "Writing {} bytes to {}".format( len( contents ), filename )
	f = open( filename, 'w' )
	f.write( contents )
	f.close()

class FileCache():
	def __init__( self, cachefile ):
		self._cachefile = cachefile
		self._cachedfiles = {}
	
	def _filerefislink( self, fileref ):
		#TODO make FileCache.filerefislink a little less insane
		if( fileref.startswith( "http://" ) or fileref.startswith( "https://" ) ):
			return True
		return False
		

	def _getfile( self, fileref ):
		if self._filerefislink( fileref ):
			#TODO deal with failures in FileCache._getfile
			return url_get( fileref )
		else:
			return open( fileref, 'r' ).read()

	def get( self, fileref, expiry = 0 ):
		#TODO  if expiry == 0 ignore it
		#TODO deal with expiry in FileCache._get
		#TODO file storage = [ grabtime, expiry, contents ] in FileCache
		filehash = md5( fileref )
		if filehash not in self._cachedfiles:
			self._cachedfiles[ filehash ] = [ 0, 0, self._getfile( fileref ) ]
			#return self._getfile( 
		else:
			return self._cachedfiles[filehash][2]
		#pass

	def delete( self, fileref ):
		#TODO: add ability to remove file from cache
		# delete from cachedfiles
		pass


def do_tasksequence( task_sequence, args, data ):
	# feed this a {} of tasks with the key as an int of the sequence, and it'll do them
	print "tasks: {}".format( sorted( task_sequence.iterkeys() ) )
	args['found'] = False
	re_tr = re.compile( "(<tr[^>]*>(.*?)</tr[^>]*>)" )
	re_table = re.compile( "(<table[^>]*>(.*?)</table[^>]*>)" )
	
	for task in sorted( task_sequence.iterkeys() ):
		print "Task {}:".format( task ),
		t = task_sequence[ task ].split( ":" )
		#print "'{}'".format( t )
		cmd = t[0]
		cmdargs = t[1]
		if( cmd == "geturi" ):
			uri = args[ 'uris' ][int( t[1] )]
			print "Grabbing uri: {}".format( uri )
			#TODO this is only a hack while offline
			data = url_get( uri )
			#data = open( 'data/page.cache', 'r' ).read()

		elif( cmd == "replace" ):
			search, replace = t[1].split( "|" )
			print "Replacing '{}' with '{}'".format( search, replace )
			data = data.replace( search, replace )
			#print data

		elif( cmd == "find_tr_with" ):
			needle = t[1]
			print "Looking for {}".format( needle )
			rows = re_tr.findall( data )
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
		
		elif( cmd == "find_table_with" ):
			needle = t[1]
			
			tables = re_table.findall( data )
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
