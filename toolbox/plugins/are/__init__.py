import re
import config
import toolbox 

class Plugin( toolbox.base_plugin ):
	def __init__( self, parent ):
		# relies on os, re, pickle
		# feed it a filename, it'll either load a pickle of the facts or create a new empty file
		toolbox.base_plugin.__init__( self, parent )
		self.pluginname = "are"
		self._filename = config.filename[self.pluginname]
		if( not self._load() ):
			self._data = {}
			#pickle.dump( self._data, open( self.filename, "wb" ) )
			self._save()
		self.re_set = re.compile( "(\S+) (are|is a) (.*)" )	


	def _handle_text( self, text ):
		# deals with a few things
		res = self.re_set.match( text )
		if( res != None ):
			#print "Found a setter: %s" % text
			#print res.groups()
			self.set( res.group(1), res.group( 3).strip() )
			return "are doesn't handle_text right yet"

	def replace( self, node, newfacts ):
		# this force-resets a node's data
		# send it a node name and an array full of facts
		self._data[node] = newfacts

	def set( self, node, newfact ):
		# adds a new fact, checks to see if it's there already 
		if( node not in self._data ):
			self._data[node] = [ newfact ]
			print "I learnt about {} and they are {}".format( node, newfact )
		elif( node in self._data ):
			if( newfact not in self._data[node] ):
				self._data[node].append( newfact )
				print "I learnt a new fact about %s, they are %s" % ( node, newfact )
			else:
				print "I knew %s are %s already!" % ( node, newfact )
		else:
			print "Something happened?"

	def get( self, node ):
		# give it a node and it'll tell you what it knows. Could get unwieldy quickly.
		if node not in self._data:
			print "I don't know about {}".format( node )
		else:
			subfacts = []
			print "This is what I know about {}".format( node )
			print "They are {}".format( ",".join( self._data[node] ) )
			for fact in [ fact for fact in self._data if fact != node ] :
				if node in self._data[fact]: 
					subfacts.append( fact )
			if len( subfacts ) > 0:
				print "Also a colour can be {}".format( ",".join( subfacts ) )



