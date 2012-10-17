#!/usr/bin/env python

try:
	import pexpect
except ImportError:
	print "Failed to import pexpect"

import config
import pickle
import re
import hashlib
import urllib2
import sys
import os
import time

class base_plugin():
	def __init__( self, parent ):
		self.pluginname = "base"
		self._parent = parent
		self._filename = ""
		self._data = ""

	def _help( self, text ):
		helptext = [ f for f in dir( self ) if not f.startswith( "_" ) and f != 'pluginname' ]
		# should probably deal with help sub commands
		return " Commands in '{}' are {}.".format( self.pluginname, ", ".join( helptext  ) )


	def _handle_text( self, text ):
		text = " ".join( text.split()[1:] )
		commands = [ func for func in dir( self ) if not func.startswith( "_" ) ]
		for f in commands:
			if text.startswith( "{}".format( f ) ):
				return eval( 'self.{}( " ".join( text.split()[1:] ) )'.format( f ) )
		return "Unsure what you meant by '{}'".format( text )

	def _load( self ):
		if( self._filename != "" ):
			if os.path.exists( self._filename ):
				self._data = pickle.load( open( self._filename , "rb" ) )
				return True
			# no file? return false
			return False
		else:
			# if the filename's not set, return False as it can't load
			return False

	def _save( self ):
		# if there's data, save it
		if( self._data != "" and self._filename != "" ):
			#save the file
			pickle.dump( self._data, open( self._filename, 'wb' ) )
		# if not, return false
		else:
			return False	


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

class FileCache( base_plugin ):
	def __init__( self, parent ):
		base_plugin.__init__( self, parent )
		self.pluginname = 'filecache'
		self._filename = config.filename[self.pluginname]
		# base datatype is [ curr_time, expiry, self._getfile( fileref ) ]
		#self._blank = [ 0, 0, None ]
		self._blank = { 'lastupdate' : 0, 'expiry' : 0, 'contents' : None, 'locked' : True } 
		self._data = {}
		self._load()

		self._re_filerefisuri = re.compile( "^[a-z]{3,5}:\/\/[\S]+", re.IGNORECASE )
		self._delexpired()
		#print self.cachenum()
		
	def _expirytime( self, filehash ):
		""" gets the time the file should expire given a hash """
		fc = self._data[filehash]
		expirytime = fc['lastupdate'] + fc['expiry']
		return expirytime


	def _expired( self, filehash ):
		""" checks if a file is expired """
		if time.time() > self._expirytime( filehash ):
			return True
		return False

	def _delexpired( self ):
		""" this goes through the cached files and deletes the expired ones """
		keys = self._data.keys()
		#print "Cleaning expired files, {} to process.".format( len( keys ) ),
		for f in keys:
			if self._expired( f ):
				del( self._data[f] )

	def _filerefisuri( self, fileref ):
		if( self._re_filerefisuri.match( fileref ) != None ):
			return True
		return False
		

	def _getfile( self, fileref ):
		if self._filerefisuri( fileref ):
			#TODO deal with failures in FileCache._getfile
			return url_get( fileref )
		else:
			return open( fileref, 'r' ).read()

	def getfile( self, fileref, expiry = 0 ):
		#TODO  if expiry == 0 ignore it
		filehash = md5( fileref )
		curr_time = time.time()
		# if the file has expired, re-get it
		getfile = False
		if ( self._data.get( filehash, None ) == None ):
			# File Not Cached
			getfile = True

		else:
			if self._expired( filehash ):
				# print "File Expired, currtime: {} expirytime: {}".format( curr_time, expirytime )
				getfile = True

		if getfile:
			# re-get the file
			self._data[ filehash ] = self._blank #[ curr_time, expiry, self._getfile( fileref ) ]
			self._data[ filehash ]['lastupdate'] = curr_time
			self._data[ filehash ]['expiry'] = expiry
			self._data[ filehash ]['contents'] = self._getfile( fileref )
			self._unlock( fileref )

		expirytime = self._data[ filehash ]['expiry'] + self._data[ filehash ]['lastupdate']
		self._data[filehash]
		return self._data[filehash]['contents']

	def _unlock( self, fileref ):
		filehash = md5( fileref )
		tmp = self._data.get( filehash, None )
		if( tmp != None ):
			self._data[filehash]['locked'] = False
			return True
		return False

	def delete( self, filehash ):
		""" deletes a hash from the file cache, not sure how often you'd actually use this """
		if self._data.get( filehash, None ) != None:
			del( self._data[filehash] )
			return True
		return False

	def cachenum( self, text=None ):
		return "Number of files cached: {}".format( len( self._data ) )

if __name__ == "__main__":
	filerefisuri = re.compile( "^[a-z]{3,5}:\/\/[\S]+", re.IGNORECASE )
	for test in [ 'http://lol.com', 'HttPs://buggts.com:80', '/hello/world' ]:
		print "{} {}".format( test, filerefisuri.match( test ) )

