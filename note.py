import config
import pickle, os
import toolbox

class Note( toolbox.base_plugin ):
	def __init__( self, parent ):
		# relies on hashlib, pickle, os
		toolbox.base_plugin.__init__( self, parent )
		self.pluginname = "note"
		self._filename = config.filename[self.pluginname]
		self._data = {}
		self.load()

	def search( self, text ):
		foundany = False
		terms = text.split()
		#print "Searching for: {}".format( ", ".join( terms ) )
		for note in self._data:
			found = False
			notelow = self._data[note]
			for term in terms:
				if( term.lower() in notelow ):
					found = True
					if not foundany:
						retval = "##################\n"
					foundany = True
					break
			if found:	
				retval += self._data[note]
				retval += "\n##################"
		if not foundany:
			return "Sorry, nothing found in {}.".format( self.pluginname )
		else:
			return retval

	
	def add( self, text ):
		h = toolbox.md5( text )
		if h not in self._data:
			self._data[h] = text
			self.save()
			return "Added"
		return "Note already exists"


