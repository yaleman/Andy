#!/usr/bin/env python

import os
import sys
import toolbox
#import config
import imp
# TODO deal with calendars, look at upcoming agenda, set alarms etc? - http://code.google.com/p/gdata-python-client/


class Andy():
	def __init__( self ):
		self.plugins = {}
		self._pluginname = "Andy"
		#to add a new plugin here, all you need to do is add its name to the list
		self._loadplugins()
		#self.register_plugin( toolbox.FileCache( self ) )
		print( "{} started.".format( self._pluginname ) )


	def _loadplugins( self ):
		""" dynamic plugin loader 
			based loosely on the tutorial here: http://lkubuntu.wordpress.com/2012/10/02/writing-a-python-plugin-api/ """
		# dynamic plugin loader
		plugindir = './toolbox/plugins'
		# search the plugin folder for files
		for f in os.listdir( plugindir ):
			location = os.path.join( plugindir, f )
			# find the module
			info = imp.find_module( '__init__', [ location ] )
			# load the module looking for Plugin 
			plugin = imp.load_module( 'Plugin', *info )
			# register it into andy
			self.register_plugin( plugin.Plugin( self ) )
			

	def _command_hash( self, text ):
		""" this handles #command style things in the interact loop """
		oper = text.lower().split()[0][1:]
		if( oper == "plugins" ):
			return ", ".join( self.plugins.keys() )
		elif( oper.startswith( "restart" ) ):
			# this should save the system state then restart andy
			print( "Shutting down..." )
			self._save_before_shutdown()
			# this should restart the program
			python = sys.executable
			print( "Restarting now..." )
			os.execl(python, python, * sys.argv)
		elif( oper.startswith( "help" ) ):
			helpterm = text.split()[1:]
			if len( helpterm ) > 0:
				#print "Looking for help on {}".format( helpterm[0] )
				if( helpterm[0] in self.plugins ):
					# see if the plugin has its own help
					if( "_help" in dir( self.plugins[helpterm[0]] ) ):
						return self.plugins[helpterm[0]]._help( text )
					else:
						helptext = [ f for f in dir( self.plugins[helpterm[0] ] ) if not f.startswith( "_" ) and f != 'pluginname' ]
						return "Commands in '{}' are {}.".format( helpterm[0], ", ".join( helptext  ) )
			else:
				return " #help [command] will give you help on a particular command\n #plugins will give you a list of plugins"
		else:
			return "Eh?"

	def interact( self ):
		""" interact is the main loop of the andybot
			it'll sit there waiting on input, if it's a #something it's probably a help/query
			anything else you type should start with a plugin name and then the subsequent commands/arguments """ 
		text = ""
		while( text != "quit" ):	
			text = raw_input( "# " ).strip()
			# skips dem newlines
			if( text != "" ):
				if text.startswith( "#" ):
					print( self._command_hash( text ) )
				else:
					text_lower = text.lower()
					oper = text_lower.split()[0]
					if( oper in self.plugins ):
						if( '_handle_text' in dir( self.plugins[oper] ) ):
							print( self.plugins[oper]._handle_text( text ) )
						else:
							print( "{} module doesn't have handle_text".format( oper ) )

		self._save_before_shutdown()

	def _save_before_shutdown( self ):
		# this goes through all the registered plugins and saves them
		for plugin in self.plugins:
			if( '_save' in dir( self.plugins[plugin] ) ):
				self.plugins[plugin]._save()
	

	def register_plugin( self, plugin ):
		# registers plugins
		# plugins need a self.pluginname which are unique so that when you call @plugin xxx it'll know what to ask for
		# doesn't hurt to have a handle_text too
		if plugin not in self.plugins:
			self.plugins[plugin.pluginname] = plugin
		else:
			print( "Plugin with name {} is already registered.".format( plugin ) )


if( __name__ == '__main__' ):

	andy = Andy()
	andy.plugins['are'].replace( "ipaddr", toolbox.self_ipaddr() )

	andy.interact()
