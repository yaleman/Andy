import config
import pickle, os
import toolbox

class Note( toolbox.base_plugin ):
	def __init__( self, parent, preload = True ):
		# relies on hashlib, pickle, os
		toolbox.base_plugin.__init__( self, parent )
		self.pluginname = "note"
		self.filename = config.filename[self.pluginname]
		self.notes = {}
		self.load( preload )
		self.changed = False

	def search( self, text ):
		foundany = False
		terms = text.split()
		#print "Searching for: {}".format( ", ".join( terms ) )
		for note in self.notes:
			found = False
			notelow = self.notes[note]
			for term in terms:
				if( term.lower() in notelow ):
					found = True
					if not foundany:
						retval = "##################\n"
					foundany = True
					break
			if found:	
				retval += self.notes[note]
				retval += "\n##################"
		if not foundany:
			return "Sorry, nothing found in {}.".format( self.pluginname )
		else:
			return retval

	
	def add( self, text ):
		h = toolbox.md5( text )
		if h not in self.notes:
			self.notes[h] = text
			self.save()
			return "Added"
		return "Note already exists"

	def load( self ):
		# loads notes from file into a variable called notes
		# if learn == True, stores the notes into self.notes
		# if the file doesn't exist, create one
		if( os.path.exists( self.filename ) ):
			self.notes = pickle.load( open( self.filename, "rb" ) )
			return self.otes
		else:
			return "Can't find file specified for Notes instance"
	def save( self, force = False ):
		# saves the file
		# checks to see if the file's changed to avoid extra writes
		# can be forced
		pickle.dump( self.notes, open( self.filename, "wb" ) )
			
