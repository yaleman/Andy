"""
ircloghandler.py
"""

import os
import re

class LogHandler():
	def __init__( self, filename ):
		self.filename = filename
		self.re_set = re.compile( "(\S+) (are|is a) ([a-zA-Z0-9\s]+)" )
		self.re_ima = re.compile( "\<[\s\@\#]{1}([a-zA-Z0-9\-\_\+]+)\>.*I'm a ([A-Za-z0-9\'\-]+)[\']{0,1}" , re.IGNORECASE )

	def process( self ):
		contents = open( self.filename, "r" ).read()
		print "{} length {}".format( self.filename, len( contents ) )
		for line in contents.split( "\n" ):
			res = self.re_set.search( line )
#			if( res != None ):
#				print "Found a setter: %s" % line
#				print res.groups()
			res = self.re_ima.search( line )
			if( res != None ):
				print "Found an ima: {}".format( line )
				print res.groups()


if __name__ == "__main__":
	datadir = "./data/irclogs/"
	for file in os.listdir( datadir ):
		loghandler = LogHandler( "{}{}".format( datadir, file ) )
		loghandler.process()
