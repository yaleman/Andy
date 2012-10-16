import config
import pickle
import os
import toolbox

class Note( toolbox.base_plugin ):
	def __init__( self, parent ):
		# relies on hashlib, pickle, os
		toolbox.base_plugin.__init__( self, parent )
		self.pluginname = "note"
		self._filename = config.filename[self.pluginname]
		self._data = {}
		self._load()

	def search( self, text ):
		foundany = False
		terms = [ term.lower() for term in text.split() ]
		# python list comprehensions are mental
		# this will return all results, if ANY term matches.
		notes = "\n##################\n".join( set( [ self._data[note] for note in self._data for term in terms if term in self._data[note].lower() ] ) )
		return notes

	
	def add( self, text ):
		h = toolbox.md5( text )
		if h not in self._data:
			self._data[h] = text
			self._save()
			return "Added"
		return "Note already exists"

	def dump( self, text ):
		for notekey in self._data:
			print "# {}".format( self._data[notekey] )
