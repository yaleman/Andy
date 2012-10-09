#!/usr/bin/python
import subprocess
import re
import pickle
import os, hashlib
# my modules
from note import Note
from are import Are

# TODO make it so modules imported can register with the Andy object so plugins can add functionality over time
# Andy.register( plugin-responder (eg @note), *handler )

# TODO sense-search-periodically - look for things over time like movies etc on x locations	

class Andy():
	def __init__( self ):
		pass
	def interact( self ):
		text = ""
		while( text != "quit" ):
			text = raw_input( "# " ).strip()
			#print "'%s'" % text
			if text.lower().startswith( "@note" ):
				notes.handle_text( text )
			else:
				are.handle_text( text )
		are.save()
		notes.save()

def self_ipaddr():
	# relies on subprocess
	# only works on POSIX systems	
	ifconfig = subprocess.check_output( "ifconfig" )
	re_ipfind = re.compile( "inet[6\s]{1,2}([a-f0-9\.\:]{3,})" )
	ipaddr = []
	for line in ifconfig.split( "\n" ):
		if "inet" in line and re_ipfind.search( line ) != None:
			ipaddr.append( re_ipfind.findall( line )[0] )
	return ipaddr

andy = Andy()
are = Are( "are.pickle" )
notes = Note( "notes.pickle" )

"""are.handle_text( "apples are green" )
are.handle_text( "apples are red" )
are.handle_text( "apples are spherical" )
are.handle_text( "red is a colour" )
are.handle_text( "green is a colour" )

are.handle_text( "colour is a noun" )
are.handle_text( "colour is a verb" )

are.get( "colour" )
"""


are.replace( "ipaddr", self_ipaddr() )
are.save()

andy.interact()
#are.save()
