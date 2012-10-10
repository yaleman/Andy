#!/usr/bin/env python
import subprocess
import re
import pickle
import os, hashlib
# my modules
#from note import Note
#from are import Are
import note, are, sense_network
import toolbox
import config


# TODO make it so modules imported can register with the Andy object so plugins can add functionality over time
# Andy.register( plugin-responder (eg @note), *handler )

# TODO sense-search-periodically - look for things over time like movies etc on x locations	

class Andy():
	def __init__( self ):
		self.plugins = {}
	def interact( self ):
		text = ""
		while( text != "quit" ):
			text = raw_input( "# " ).strip()
			#print "'%s'" % text
			text_lower = text.lower()
			if text_lower.startswith( "#" ):
				oper = text_lower.split()[0][1:]
				if( oper == "plugins" ):
					print ", ".join( self.plugins.keys() )
				elif( oper.startswith( "help" ) ):
					helpterm = text.split()[1:]
					if len( helpterm ) > 0:
						print "Looking for help on {}".format( helpterm[0] )
						if( helpterm[0] in self.plugins ):
							helptext = [ f for f in dir( self.plugins[helpterm[0] ] ) if not f.startswith( "_" ) ]
							print "Commands in {} are {}.".format( helpterm[0], helptext  )
			elif text_lower.startswith( "@" ):
				oper = text_lower.split()[0][1:]
				if( oper in self.plugins ):
					if( 'handle_text' in dir( self.plugins[oper] ) ):
						print self.plugins[oper].handle_text( text )
					else:
						print "{} module doesn't have handle_text".format( oper )
				else:
					print "Can't find {} module".format( oper )
			else:
				are.handle_text( text )
		# this goes through all the registered plugins and saves them
		for plugin in self.plugins:
			if( 'save' in dir( self.plugins[plugin] ) ):
				self.plugins[plugin].save()
	
	def register_plugin( self, plugin ):
		# registers plugins
		# plugins need a self.pluginname which are unique so that when you call @plugin xxx it'll know what to ask for
		# doesn't help to have a handle_text too
		if plugin not in self.plugins:
			self.plugins[plugin.pluginname] = plugin



if( __name__ == '__main__' ):

	andy = Andy()

	are = are.Are( "are.pickle" )
	note = note.Note( "notes.pickle" )
	andy.register_plugin( sense_network.SenseNetwork( config ) )
	andy.register_plugin( are )
	andy.register_plugin( note )

	are.replace( "ipaddr", toolbox.self_ipaddr() )
	are.save()


	andy.interact()
