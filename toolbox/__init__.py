#!/usr/bin/env python


import subprocess
import config
import pickle
import re
import hashlib
import urllib.request
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
		if( text.strip() != "" ):
			cmd = text.split()[0]
			if cmd in commands:
				return getattr( self, cmd )( " ".join( text.split()[1:] ) )
			return "Unsure what you meant by '{}'".format( text )
		else:
			return "Got a task to do?"

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

#http://stackoverflow.com/questions/567542/running-a-command-as-a-super-user-from-a-python-script
# TODO: reimplement sudorun at some point
#def sudorun( command, password ):
	# uses pexpect to run a command with sudo on the command line with a given password and return the results. 
	# relies on pexpect
#	child = pexpect.spawn ( "sudo {}".format( command ) )
#	i = child.expect( [ 'Password:*', '' ] )
#	lines = []
#	if i == 0:
#		child.sendline( password )
#	else:
#		lines.append( child.before.strip() )
#	while not child.eof() :
#		lines.append( child.readline().strip() )
#	return lines

def run( command, getstderror = False ):
	""" this will run a given command on the commandline """
	torun = command.split()
	
	if( getstderror ): #include STDERR into the data
		stderr = subprocess.STDOUT
	else:
		stderr = None
	try:
		retval = subprocess.check_output( torun, stderr=stderr )
	except subprocess.CalledProcessError as e :
		retval = e.output
	return retval.decode( 'utf-8' )
	#return lines

def self_ipaddr():
	""" finds and returns list of the local ip addresses for all interfaces
		relies on subprocess, only works on POSIX systems """
	ifconfig = run( "ifconfig" )
	re_ipfind = re.compile( "inet[6\s]{1,2}([a-f0-9\.\:]{3,})" )
	ipaddr = []
	#print ifconfig
	for line in ifconfig.split( '\n' ):
		if "inet" in line :
			if re_ipfind.search( line ) != None:
				ipaddr.append( re_ipfind.findall( line )[0] )
	return ipaddr

def url_get( url ):
	""" grabs a url and returns the contents
		based on info from here: http://docs.python.org/library/urllib2.html#urllib2.urlopen """
	# create the request object
	#TODO deal with exceptions in url.get (deals with URLError so far)
	#try:
	u = urllib.request.urlopen( url )
		#u = urllib2.urlopen( url )
	return u.read()
#	except:
#		print( "Whoops, URL get failed" )
#		return ""
	#except urllib.error as e :
	#	print( "URL Access Error: {}".format( e ) )
	#	#u.geturl() should return whatever ended up being grabbed (In case of a redirect)


def md5( tohash ):
	""" returns an md5 hash of the input text """
	h = hashlib.new( 'ripemd160' )
	h.update( tohash.encode( 'utf-8' ) )
	return h.hexdigest()

def writefile( filename, contents ):
	message = "Writing {} bytes to {}".format( len( contents ), filename )
	print( message )
	try:
		f = open( filename, 'w' )
		f.write( contents )
		f.close()
	except( IOError ):
		print( "IOError Error writing file" )
	return True


