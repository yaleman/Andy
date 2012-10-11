#!/usr/bin/env python

try:
	import pexpect
except ImportError:
	print "Failed to import pexpect"

#import subprocess
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
	u = urllib2.urlopen( url )
	# u.geturl() should return whatever ended up being grabbed (In case of a redirect)
	return u.read()

def md5( text ):
	h = hashlib.new( 'ripemd160' )
	h.update( text )
	return h.hexdigest()
