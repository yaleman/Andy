#!/usr/bin/python
"""
ircloghandler.py
"""

import os
import re

class LogHandler():
	def __init__( self, filename ):
		self.filename = filename
		self.re_irclog = re.compile( "[0-9\:\s]{0,5}\<[\s\@\#]{0,1}([a-zA-Z0-9\-\_\+]+)\>(.*)", re.IGNORECASE )
		self.re_set = re.compile( "(\S+) (are|is a) ([a-zA-Z0-9\s]+)" )
		self.re_ima = re.compile( "\<[\s\@\#\+]{1}([a-zA-Z0-9\-\_\+]+)\>.*I'm a ([A-Za-z0-9\'\-\/\\\_]+)[\']{0,1}" , re.IGNORECASE )
		self.re_uri = re.compile( "[\s]+([a-z]{3,5}\:\/\/[\S]+)", re.IGNORECASE )


	def process( self ):
		peopletalking = {}
		contents = open( self.filename, "r" ).read()
		print( "{} length {}".format( self.filename, len( contents ) ) )
		for line in contents.split( "\n" ):
			logline = self.re_irclog.search( line )
			if logline != None:
				nick, text = logline.groups()
				uri_list = self.re_uri.findall( text )
				if uri_list:
					print( uri_list )
		#		print nick.strip(), text.strip()
				if( nick not in peopletalking ):
					peopletalking[nick] = [text]
				else:
					peopletalking[nick].append( text )
#			continue
#			res = self.re_set.search( line )
#			if( res != None ):
#				print "Found a setter: %s" % line
#				print res.groups()
			res = self.re_ima.search( line )
			if( res != None ):
				#print "Found an ima: {}".format( line )
				groups = res.groups()
				if groups[ 0 ] == "yaleman":
					print( groups, line )
		
		print( [ key for key in peopletalking ] )

if __name__ == "__main__":
	datadir = "./data/irclogs/"
	for file_name in os.listdir( datadir ):
		loghandler = LogHandler( "{}{}".format( datadir, file_name ) )
		loghandler.process()
