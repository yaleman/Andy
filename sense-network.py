#!/usr/bin/env python

try:
	import pexpect
except ImportError:
	print "Couldn't load pexpect"
import re
import toolbox
import config

command = "lsof -i4 -L -n -P"

import json

#TODO: deal with ipv6 ('launchd', '1', 'root', '32u', 'IPv6', '0x78aab92d3c18db51', '0t0', 'TCP', '[::1]:631 (LISTEN)')

lineparser = re.compile( "(?P<command>[a-zA-Z0-9]+)[\s]+(?P<pid>[0-9]+)[\s]+(?P<username>[\S]+)[\s]+([a-zA-Z0-9]+)[\s]+(?P<sixorfour>[A-Za-z0-9]+)[\s]+(?P<device>[a-zA-Z0-9]+)[\s]+(?P<size>[a-z0-9A-Z]+)[\s]+(?P<transport>[A-Za-z0-9]+)[\s]+(?P<details>.*)" )


def parse_lsof_information( lines ):
	errors = []
	info = []
	for line in lines:
		if line != "" and not line.startswith( "COMMAND " ):
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
				elif( "(" in details ):
					details = details.replace( ")", "" ).replace( "(", "" )
					srcdest, status = details.split()
					src, dest = srcdest.split( ":" )
				else:
					src, dest = details.split( ":" )
				src = src.split( ":" )
				dest = dest.split( ":" )
				status = status.replace( ")", "" ).replace( "(", "" )
				info.append( [src, dest, status] )
	return errors, info

errors, lines = toolbox.sudorun( command, config.password )
errors, info = parse_lsof_information( lines )

#for line in info:
#	print line
print json.dumps( info )

if( len( errors ) > 0 ):
	print "#" * 50
	print "      Errors"
	print "#" * 50
	print "\n".join( errors )

