import config
import pickle, os
import toolbox

class Note( config.base_plugin ):
	def __init__( self, parent, filename, preload = True ):
		# relies on hashlib, pickle, os
		config.base_plugin.__init__( self, parent )
		self.filename = filename
		self.notes = {}
		self.load( preload )
		self.changed = False
		self.pluginname = "note"

	def __del__( self ):
		#print "Saving notes on destruction"
		#pickle.dump( self.notes, open( self.filename, "wb" ) )
		pass

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
			self.changed = True
			#return True
			return "Added"
		#return False
		return "Note already exists"

	def load( self, learn = True ):
		# loads notes from file into a variable called notes
		# if learn == True, stores the notes into self.notes
		# if the file doesn't exist, create one
		if( os.path.exists( self.filename ) ):
			notes = pickle.load( open( self.filename, "rb" ) )
			if( learn ):
				self.notes = notes
				self.changed = False
			return notes
		else:
			self.save( True )

	def save( self, force = False ):
		# saves the file
		# checks to see if the file's changed to avoid extra writes
		# can be forced
		if( self.changed or force == True ):
			pickle.dump( self.notes, open( self.filename, "wb" ) )
			self.changed = False
			
