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
		fc = self._data.get( filehash, None )
		if fc != None:
			# if expiry's -1, return that
			if fc['expiry'] == -1:
				return -1

			else:
				expirytime = fc['lastupdate'] + fc['expiry']
				return expirytime
		return False


	def _expired( self, filehash ):
		""" checks if a file is expired, if it's set to -1, it'll never expire """
		expirytime = self._expirytime( filehash )
		if( expirytime == False ):
			pass
			#TODO Raise error in filecache._expired on can't find hash
		if self._expirytime( filehash ) == -1:
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
		""" checks if file ref is uri... should work in 99% of cases """
		if( self._re_filerefisuri.match( fileref ) != None ):
			return True
		return False
		

	def _getfile( self, fileref ):
		if self._filerefisuri( fileref ):
			#TODO deal with failures in FileCache._getfile
			return toolbox.url_get( fileref )
		else:
			try:
				retval = open( fileref, 'r' ).read()
				return retval
			except( IOError ):
				print( "IOError accessing {}".format( fileref ) )

	def getfile( self, fileref, expiry = config.filecache['defaultexpiry'] ):
		""" gets a file from cache """
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

		#expirytime = self._data[ filehash ]['expiry'] + self._data[ filehash ]['lastupdate']
		# TODO not sure why expirytime's above?
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

