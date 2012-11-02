import time
import config
import pickle
import os
import toolbox

class Plugin( toolbox.base_plugin ):
	def __init__( self, parent ):
		""" this is the note taking and storing plugin """
		# relies on hashlib, pickle, os
		toolbox.base_plugin.__init__( self, parent )
		self.pluginname = "note"
		self._filename = config.filename[self.pluginname]
		self._data = {}
		self._load()

	def search( self, text ):
		""" search for a given note in the database, doesn't do ranking or anything yet """
		terms = [ term.lower() for term in text.split() ]
		# python list comprehensions are mental and fun!
		# this will return all results, if ANY term matches.
		notes = "\n".join( set( [  "#{} {}#\n{}".format( self._data[note]['time'], note, self._data[note]['contents'] ) for note in self._data for term in terms if term in self._data[note]['contents'].lower() ] ) )
		return notes

	
	def add( self, text ):
		""" adds a new note, won't allow you to add duplicates """
		if( text.strip() != "" ):
			notehash = toolbox.md5( text )
			if notehash not in self._data:
				self._data[notehash] = { 'contents' : text, 'time' : time.time() }
				self._save()
				return "Added"
			return "Note already exists"

	def dump( self, text ):
		""" dump a full list of all the notes """
		for notekey in self._data:
			print( "- {} {}".format( notekey, self._data[notekey]['time'] ) )
			print( "# {}".format( self._data[notekey]['contents'] ) )

	def delete( self, text ):
		""" delete a note based on a given noteid """
		if len( text.split() ) == 1 :
			noteid = text.strip()
			if noteid in self._data:
				del( self._data[noteid] )
				return "Deleted NoteID {}".format( noteid )
			else:
				return "NoteID {} not found in data.".format( noteid )
		else:
			return "Too many commands entered or something: '{}'".format( text )
