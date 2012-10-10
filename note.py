import hashlib, pickle, os

class Note():
	def __init__( self, filename, preload = True ):
		# relies on hashlib, pickle, os
		self.filename = filename
		self.notes = {}
		self.load( preload )
		self.changed = False
		self.pluginname = "note"

	def __del__( self ):
		#print "Saving notes on destruction"
		#pickle.dump( self.notes, open( self.filename, "wb" ) )
		pass

	def handle_text( self, text ):
		text = " ".join( text.split()[1:] )
		if text.lower().startswith( "add" ):
			self.add( " ".join( text.split()[1:] ) )
		elif text.lower().startswith( "search" ):
			foundany = False
			terms = text.split()[1:]
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
		else:
			return "Unsure what you meant by '{}'".format( text )

	def add( self, text ):
		# generate hash of note
		h = hashlib.new( 'ripemd160' )
		h.update( text )
		h = h.hexdigest()
		# check if hash not in notes storage
		if h not in self.notes:
			self.notes[h] = text
			self.changed = True
			return True
		return False

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
			try:
				self.changed = False
			except:
				pass

