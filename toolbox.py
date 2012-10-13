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



