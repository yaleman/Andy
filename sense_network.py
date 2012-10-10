#!/usr/bin/env python

try:
	import pexpect
except ImportError:
	print "Couldn't load pexpect"
import re
import toolbox
import config


import json

#TODO: deal with ipv6 ('launchd', '1', 'root', '32u', 'IPv6', '0x78aab92d3c18db51', '0t0', 'TCP', '[::1]:631 (LISTEN)')

class SenseNetwork():
	"""  this should be run every x time to check up on what the computer's doing and report back to the database
		 the basic idea is to get a map of process -> ports/ip's used. things like web browsers will be noisy, but I'm looking
		 for those strange apps/ports that you don't know about until you're looking on wireshark.
		"""

	def __init__( self, config ):
		self.lineparser = re.compile( "(?P<command>[a-zA-Z0-9]+)[\s]+(?P<pid>[0-9]+)[\s]+(?P<username>[\S]+)[\s]+([a-zA-Z0-9]+)[\s]+(?P<sixorfour>[A-Za-z0-9]+)[\s]+(?P<device>[a-zA-Z0-9]+)[\s]+(?P<size>[a-z0-9A-Z]+)[\s]+(?P<transport>[A-Za-z0-9]+)[\s]+(?P<details>.*)" )
		self.command = "lsof -i4 -L -n -P"
		self.config = config
		self.info = []
		self.errors = []
		self.pluginname = "sense-network"
		

	def getinfo( self ):
		if self.info:
			return self.info
		else:
			return self.parse_lsof_information()[1]
	def geterrors( self ):
		if self.errors:
			return self.errors
		else:
			return self.parse_lsof_information()[0]

	def handle_text( self, text ):
		return "This isn't really supported by {}, sorry".format( self.pluginname )

	def parse_lsof_information( self ):
		errors, lines = toolbox.sudorun( self.command, self.config.password )
		errors = []
		info = []
		for line in lines:
			if line != "" and not line.startswith( "COMMAND " ):
				parsed = self.lineparser.findall( line )[0]
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
					info.append( [ det for det in parsed[:-1] ] + [src] + [dest] + [status ] )
		self.info = info
		self.errors = errors
		return errors, info

if( __name__ == '__main__' ):

	senseNetwork = SenseNetwork( config )
	#errors, info = senseNetwork.parse_lsof_information()
	errors = senseNetwork.geterrors()
	info = senseNetwork.getinfo()

	dets = {}
	for line in info:
		#print line
		if line[0] not in dets:
			dets[line[0]] = [ line[1:] ]
		else:
			dets[line[0]].append( line[1:] )
	for line in dets:
		print line, dets[line]
		print ""
	#print json.dumps( info, indent=2 )

	if( len( errors ) > 0 ):
		print "#" * 50
		print "      Errors"
		print "#" * 50
		print "\n".join( errors )

