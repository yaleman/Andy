import time
import re
import os
import sys 
import toolbox
import config

class Plugin( toolbox.base_plugin ):
	def __init__( self, parent ):
		toolbox.base_plugin.__init__( self, parent )
		self.pluginname = 'filecache'
		self._filename = config.filename[self.pluginname]
		# base datatype is [ curr_time, expiry, self._getfile( fileref ) ]
		#self._blank = [ 0, 0, None ]
		self._blank = { 'lastupdate' : 0, 'expiry' : 0, 'contents' : None, 'locked' : True } 
		self._data = {}
		self._load()

		self._re_filerefisuri = re.compile( "^[a-z]{3,5}:\/\/[\S]+", re.IGNORECASE )
		self._delexpired()
		#print self.cachenum()
		
	def _expirytime( self, filehash ):
		""" gets the time the file should expire given a hash """
		fc = self._data[filehash]
		expirytime = fc['lastupdate'] + fc['expiry']
		return expirytime


	def _expired( self, filehash ):
		""" checks if a file is expired, if it's set to -1, it'll never expire """
		if self._data[filehash]['expiry'] == -1:
			return False
		if time.time() > self._expirytime( filehash ):
			return True
		return False

	def _delexpired( self ):
		""" this goes through the cached files and deletes the expired ones """
		keys = self._data.keys()
		#print "Cleaning expired files, {} to process.".format( len( keys ) ),
		for f in keys:
			if self._expired( f ):
				del( self._data[f] )

	def _filerefisuri( self, fileref ):
		if( self._re_filerefisuri.match( fileref ) != None ):
			return True
		return False
		

	def _getfile( self, fileref ):
		if self._filerefisuri( fileref ):
			#TODO deal with failures in FileCache._getfile
			return toolbox.url_get( fileref )
		else:
			return open( fileref, 'r' ).read()

	def getfile( self, fileref, expiry = 0 ):
		#TODO  if expiry == 0 ignore it
		filehash = self._genhash( fileref )
		curr_time = time.time()
		# if the file has expired, re-get it
		getfile = False
		if ( self._data.get( filehash, None ) == None ):
			# File Not Cached
			getfile = True

		else:
			if self._expired( filehash ):
				# print "File Expired, currtime: {} expirytime: {}".format( curr_time, expirytime )
				getfile = True

		if getfile:
			# re-get the file
			self._data[ filehash ] = self._blank #[ curr_time, expiry, self._getfile( fileref ) ]
			self._data[ filehash ]['lastupdate'] = curr_time
			self._data[ filehash ]['expiry'] = expiry
			self._data[ filehash ]['contents'] = self._getfile( fileref )
			self._unlock( fileref )

		expirytime = self._data[ filehash ]['expiry'] + self._data[ filehash ]['lastupdate']
		self._data[filehash]
		return self._data[filehash]['contents']

	def _genhash( self, fileref ):
		return toolbox.md5( fileref )

	def _cached( self, filehash ):
		if self._data.get( filehash, None ) != None:
			return True
		return False

	def __setlock( self, lock, fileref=None, filehash=None ):
		if fileref != None and filehash == None:
			filehash = self._genhash( fileref )
		elif filehash == None:
			return None
		if not self._cached( filehash ):
			return None
		elif isinstance( lock, bool ):
			self._data[filehash]['locked'] = lock
			return lock

	def _lock( self, fileref=None, filehash=None ):
		return self.__setlock( True, fileref=fileref, filehash=filehash )

	def _unlock( self, fileref=None, filehash=None ):
		""" resets the locking on a cached file """
		return self.__setlock( False, fileref=fileref, filehash=filehash )

	def _contentlength( self, filehash ):
		""" returns the size of the stored content, ignoring metadata """
		return len( self._data[filehash]['contents'] )

	def debugfile( self, fileref ):
		filehash = self._genhash( fileref )
		if not self._cached( filehash ):
			return "File '{}' (hash: {}) not cached.".format( fileref, filehash )
		else:
			retstr = "{}\n".format( filehash )
			for key in self._data[filehash]:
				retstr += "{} : {}\n".format( key, self._data[filehash][key] )
			retstr += "Content length: {}".format( self._contentlength( filehash ) )
			return retstr 

	def delete( self, filehash ):
		""" deletes a hash from the file cache, not sure how often you'd actually use this """
		if self._data.get( filehash, None ) != None:
			del( self._data[filehash] )
			return True
		return False

	def cachenum( self, text=None ):
		return "Number of files cached: {}".format( len( self._data ) )

