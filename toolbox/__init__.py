#!/usr/bin/env python

try:
	import pexpect
except ImportError:
	print "Failed to import pexpect"

#import subprocess
import config
import pickle
import re, hashlib
import urllib2
import sys, os
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
		self._data = {}
		self._load()
		print self.cachenum()
		self._re_filerefislink = re.compile( "[a-zA-Z]{3,4}:\/\/[\S]*" )
	
	def _filerefislink( self, fileref ):
		#TODO make FileCache.filerefislink a little less insane
#		if( fileref.startswith( "http://" ) or fileref.startswith( "https://" ) ):
		if( self._re_filerefislink.match( fileref ) != None ):
			return True
		return False
		

	def _getfile( self, fileref ):
		if self._filerefislink( fileref ):
			#TODO deal with failures in FileCache._getfile
			return url_get( fileref )
		else:
			return open( fileref, 'r' ).read()

	def getfile( self, fileref, expiry = 0 ):
		#TODO  if expiry == 0 ignore it
		#TODO have something that goes through and deletes expired files - this stops the cache size bloating over time
		filehash = md5( fileref )
		curr_time = time.time()
		# if the file has expired, re-get it
		getfile = False
		if ( self._data.get( filehash, None ) == None ):
			# File Not Cached
			getfile = True


		else:
			expirytime = self._data[ filehash ][1] + self._data[ filehash ][0]
			if( curr_time > expirytime ):
				# print "File Expired, currtime: {} expirytime: {}".format( curr_time, expirytime )
				getfile = True

		if getfile:
			# re-get the file
			self._data[ filehash ] = [ curr_time, expiry, self._getfile( fileref ) ]

		expirytime = self._data[ filehash ][1] + self._data[ filehash ][0]
		#print "Didn't expire: currtime {} expirytime {}".format( curr_time, expirytime )
		#print "Seconds to go: {}".format( expirytime - curr_time )
		return self._data[filehash][2]

	def delete( self, fileref ):
		#TODO: add ability to remove file from cache
		# delete from cachedfiles
		pass

	def cachenum( self, text=None ):
		return "Number of files cached: {}".format( len( self._data ) )

