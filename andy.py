#!/usr/bin/env python

# my modules
#from note import Note
#from are import Are
import note, are
import sense_ap, sense_network, sense_todo, sense_lookfor
import toolbox
import config

#TODO add usage details for help

class Andy():
	def __init__( self ):
		self.plugins = {}

	def _command_hash( self, text ):
		oper = text.lower().split()[0][1:]
		if( oper == "plugins" ):
			return ", ".join( self.plugins.keys() )
		elif( oper.startswith( "help" ) ):
			helpterm = text.split()[1:]
			if len( helpterm ) > 0:
				#print "Looking for help on {}".format( helpterm[0] )
				if( helpterm[0] in self.plugins ):
					helptext = [ f for f in dir( self.plugins[helpterm[0] ] ) if not f.startswith( "_" ) and f != 'pluginname' ]
					return "Commands in '{}' are {}.".format( helpterm[0], ", ".join( helptext  ) )
		else:
			return "Eh?"

	def interact( self ):
		text = ""
		while( text != "quit" ):
			text = raw_input( "# " ).strip()
			#print "'%s'" % text
			text_lower = text.lower()
			if text_lower.startswith( "#" ):
				print self._command_hash( text )
			#elif text_lower.startswith( "@" ):
			oper = text_lower.split()[0][1:]
			if( oper in self.plugins ):
				if( '_handle_text' in dir( self.plugins[oper] ) ):
					print self.plugins[oper]._handle_text( text )
				else:
					print "{} module doesn't have handle_text".format( oper )
				#else:
				#	print "Can't find {} module".format( oper )
			#else:
			#	are._handle_text( text )
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
	andy.register_plugin( sense_network.SenseNetwork( andy ) )
	andy.register_plugin( are.Are( config.filename['are'] ) )
	andy.register_plugin( note.Note( andy, config.filename['note'] ) )
	andy.register_plugin( sense_ap.AP( andy ) )
	andy.register_plugin( sense_todo.Todo( andy ) )
	#andy.register_plugin( sense_lookfor.LookFor( lookfor_uris ) )
	
	andy.plugins['are'].replace( "ipaddr", toolbox.self_ipaddr() )
	andy.plugins['are'].save()


	andy.interact()
