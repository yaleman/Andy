#!/usr/bin/env python
import subprocess
import re
import pickle
import os, hashlib
# my modules
#from note import Note
#from are import Are
import note, are
import toolbox


# TODO make it so modules imported can register with the Andy object so plugins can add functionality over time
# Andy.register( plugin-responder (eg @note), *handler )

# TODO sense-search-periodically - look for things over time like movies etc on x locations	

class Andy():
	def __init__( self ):
		self.plugins = []
	def interact( self ):
		text = ""
		while( text != "quit" ):
			text = raw_input( "# " ).strip()
			#print "'%s'" % text
			if text.lower().startswith( "@note" ):
				note.handle_text( text )
			else:
				are.handle_text( text )
		# this goes through all the registered plugins and saves them
		for plugin in self.plugins:
			if( 'save' in dir( plugin ) ):
				plugin.save()
	
	def register_plugin( self, plugin ):
		if plugin not in self.plugins:
			self.plugins.append( plugin )



andy = Andy()
are = are.Are( "are.pickle" )
note = note.Note( "notes.pickle" )
andy.register_plugin( are )
andy.register_plugin( note )

are.replace( "ipaddr", toolbox.self_ipaddr() )
are.save()

andy.interact()
