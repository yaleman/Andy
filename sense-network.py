#!/usr/bin/env python

import pexpect, re
import config
command = "sudo lsof -i"


lineparser = re.compile( "(?P<command>[a-zA-Z0-9]+)[\s]+(?P<pid>[0-9]+)[\s]+(?P<username>[\S]+)[\s]+([a-zA-Z0-9]+)[\s]+(?P<sixorfour>[A-Za-z0-9]+)[\s]+(?P<device>[a-zA-Z0-9]+)[\s]+(?P<size>[a-z0-9A-Z]+)[\s]+(?P<transport>[A-Za-z0-9]+)[\s]+(?P<details>.*)" )


def getinformation():
	child = pexpect.spawn ( command )
	i = child.expect( ['COMMAND*', 'Password:*' ] )
	errors = []
	if i == 1:
		print "Found password request, responding"
		child.sendline( config.password )
	else:
		print "Parsing"
		child.readline()
		# start parsing 
	lines = []
	while not child.eof():
		line = child.readline().strip()
		lines.append( line )
	return errors, lines

def parseinformation( lines ):
	errors = []
	info = []
	for line in lines:
		if line != "":
			parsed = lineparser.findall( line )[0]
			if len( parsed ) == 0:
				errors.append( "FAULT: {}".format( line ) )
			else:
				details = parsed[-1]
				src, dest, status = ( "", "", "" )
				if( "->" in details ):
					src, dest = details.split( "->" )
					if( "(" in dest ):
						dest, status = dest.split()
					#print "-> src: {}".format( src )
					#print "   dst: {}".format( dest )
				elif( "(" in details ):
					#pass
					details = details.replace( ")", "" ).replace( "(", "" )
					srcdest, status = details.split()
					src, dest = srcdest.split( ":" )
					#print "()", details.split()[-1], details.split( ":" )[-1]
					#print src, dest, status
				else:
					src, dest = details.split( ":" )
					#print "?? src: {} dst: {}".format( src, dest )
				src = src.split( ":" )
				dest = dest.split( ":" )
				status = status.replace( ")", "" ).replace( "(", "" )
				info.append( [src, dest, status] )
				#print "'{}' '{}' '{}'".format( src, dest, status )
	return errors, info

errors, lines = getinformation()
errors, info = parseinformation( lines )

for line in [ line for line in info if line[-1] == "CLOSED" ]:
	print line

if( len( errors ) > 0 ):
	print "#" * 50
	print "      Errors"
	print "#" * 50
	print "\n".join( errors )
"""
child.expect ('Name .*: ')

child.expect('password:')
   child.sendline (my_secret_password)
   # We expect any of these three patterns...
   i = child.expect (['Permission denied', 'Terminal type', '[#\$] '])
   if i==0:
       print 'Permission denied on host. Can't login'
       child.kill(0)
   elif i==2:
       print 'Login OK... need to send terminal type.'
       child.sendline('vt100')
       child.expect ('[#\$] ')
   elif i==3:
       print 'Login OK.'
       print 'Shell command prompt', child.after
"""
