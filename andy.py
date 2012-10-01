#!/usr/bin/python
import subprocess
import re
import pickle
import os, hashlib
import note
	

class Are():
	def __init__( self, filename ):
		# feed it a filename, it'll either load a pickle of the facts or create a new empty file
		self.filename = filename
		if os.path.exists( self.filename ):
			self.facts = pickle.load( open( self.filename, "rb" ) )
		else:
			self.facts = {}
			#pickle.dump( self.facts, open( self.filename, "wb" ) )
			self.save()
		self.re_set = re.compile( "(\S+) (are|is a) (.*)" )	

	def save( self ):
		# save the file
		print "Saving facts"
		pickle.dump( self.facts, open( self.filename, "wb" ) )


	def handle_text( self, text ):
		# deals with a few things
		res = self.re_set.match( text )
		if( res != None ):
			#print "Found a setter: %s" % text
			#print res.groups()
			self.set( res.group(1), res.group( 3).strip() )

	def replace( self, node, newfacts ):
		# this force-resets a node's data
		# send it a node name and an array full of facts
		self.facts[node] = newfacts
		self.changed = True

	def set( self, node, newfact ):
		# adds a new fact, checks to see if it's there already 
		if( node not in self.facts ):
			self.facts[node] = [ newfact ]
			print "I learnt about {} and they are {}".format( node, newfact )
		elif( node in self.facts ):
			if( newfact not in self.facts[node] ):
				self.facts[node].append( newfact )
				print "I learnt a new fact about %s, they are %s" % ( node, newfact )
			else:
				print "I knew %s are %s already!" % ( node, newfact )
		else:
			print "Something happened?"

	def get( self, node ):
		# give it a node and it'll tell you what it knows. Could get unwieldy quickly.
		if node not in self.facts:
			print "I don't know about {}".format( node )
		else:
			subfacts = []
			print "This is what I know about {}".format( node )
			print "They are {}".format( ",".join( self.facts[node] ) )
			for fact in [ fact for fact in self.facts if fact != node ] :
				if node in self.facts[fact]: 
					subfacts.append( fact )
			if len( subfacts ) > 0:
				print "Also a colour can be {}".format( ",".join( subfacts ) )


def runProcess(exe):    
    p = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while(True):
      retcode = p.poll() #returns None while subprocess is running
      line = p.stdout.readline()
      yield line
      if(retcode is not None):
        break


def interact():
	text = ""
	while( text != "quit" ):
		text = raw_input( "# " ).strip()
		#print "'%s'" % text
		if text.lower().startswith( "@note" ):
			notes.handle_text( text )
		else:
			are.handle_text( text )
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

are = Are( "are.facts" )
notes = note.Note( "notes.note" )
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

#are.get( "ipaddr" )

interact()
are.save()
