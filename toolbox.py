#!/usr/bin/env python

try:
	import pexpect
except ImportError:
	print "Failed to import pexpect"

def sudorun( command ):
	child = pexpect.spawn ( command )
	i = child.expect( [ 'Password:*', '' ] )
	errors = []
	lines = []
	if i == 0:
		#print "Found password request, responding"
		child.sendline( config.password )
	else:
		lines.append( child.before.strip() )
	while not child.eof() :
		lines.append( child.readline().strip() )
	return errors, lines


