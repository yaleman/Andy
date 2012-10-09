#!/usr/bin/env python

try:
	import pexpect
except ImportError:
	print "Failed to import pexpect"

def sudorun( command, password ):
	# uses pexpect to run a command with sudo on the command line with a given password and return the results.
	child = pexpect.spawn ( "sudo {}".format( command ) )
	i = child.expect( [ 'Password:*', '' ] )
	errors = []
	lines = []
	if i == 0:
		child.sendline( config.password )
	else:
		lines.append( child.before.strip() )
	while not child.eof() :
		lines.append( child.readline().strip() )
	return errors, lines


