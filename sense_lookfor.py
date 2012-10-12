#!/usr/bin/env python

try:
	import pexpect
except ImportError:
	print "Couldn't load pexpect"
import re
import toolbox
import config

tasklet_idea = """
tasklet

uri:[hash] = uri (http://www.google.com)

data = download contnts from uri:[hash]


regex:[hash] = "(<?P=trtotal\<tr(?P=trinner.*)\>(?P=trcontents)</tr>)" etc
re.compile( regex:[hash] )
tr's = apply the regex to the data
"""

class LookFor( config.base_plugin ):
	def __init__( self, uris, config=config ):
		config.base_plugin.__init__( self, parent )
		self._config = config
		self.pluginname = "sense_lookfor"
		self._uris = uris
		# tr 
		self.tr = """<tr name="hover" class="forum_header_border">
          <td width="35" class="forum_thread_post"><a href="/shows/257/south-park/"><img src="http://ezimg.it/s/1/3/show_info.png" border="0" alt="Show" title="Show Description about South Park"></a><a href="http://www.tvrage.com/South_Park/episodes/1065175478" target="_blank" title="More info about South Park S16E10 PROPER HDTV x264-2HD at tvrage.com" alt="More info about South Park S16E10 PROPER HDTV x264-2HD at tvrage.com"><img src="http://ezimg.it/s/2/1/tvrage.png" width="16" height="16" border="0"></a></td>
            <td class="forum_thread_post">
                <a href="/ep/38546/south-park-s16e10-proper-hdtv-x264-2hd/" title="South Park S16E10 PROPER HDTV x264-2HD (82.29 MB)" alt="South Park S16E10 PROPER HDTV x264-2HD (82.29 MB)" class="epinfo">South Park S16E10 PROPER HDTV x264-2HD</a>
            </td>
          <td align="center" class="forum_thread_post"><a href="magnet:?xt=urn:btih:G3333GDQY3PWXHL3TG634EMBUY7IGDN4&amp;dn=South.Park.S16E10.PROPER.HDTV.x264-2HD&amp;tr=udp://tracker.openbittorrent.com:80/" class="magnet" title="Magnet Link"></a><a href="http://torrent.zoink.it/South.Park.S16E10.PROPER.HDTV.x264-2HD.[eztv].torrent" class="download_1" title="Download Mirror #1"></a><a href="http://torrents.thepiratebay.se/7716085/South_Park_S16E10_PROPER_HDTV_x264-2HD.7716085.TPB.torrent" class="download_2" title="Download Mirror #2"></a><a href="http://extratorrent.com/torrent_download/2831685/South+Park+S16E10+PROPER+HDTV+x264-2HD+%5Beztv%5D.torrent" class="download_3" title="Download Mirror #3"></a><a href="http://www.bt-chat.com/download1.php?id=163590" class="download_4" title="Download Mirror #4"></a><a href="http://torrage.com/torrent/36F7BD9870C6DF6B9D7B99BDBE1181A63E830DBC.torrent" class="download_5" title="Download Mirror #5"></a><a href="http://zoink.it/torrent/36F7BD9870C6DF6B9D7B99BDBE1181A63E830DBC.torrent" class="download_6" title="Download Mirror #6"></a>      </td>
            <td align="center" class="forum_thread_post">5h 22m </td>
            <td align="center" class="forum_thread_post_end"><a href="/forum/27786/south-park-s16e10-proper-hdtv-x264-2hd/"><img src="http://ezimg.it/s/1/3/chat_messages.png" border="0" width="16" height="16" alt="4 comments" title="4 forum comments"></a></td>
        </tr>"""

	def listuris( self ):
		return self._uris

	def uri_id( self, uri ):
		#TODO: add search for uri
		return False


if( __name__ == '__main__' ):
	lookfor_uris = { 1 : 'http://eztv.it/sort/100/' }
	lf = LookFor( None, lookfor_uris )
	re_tr = re.compile( "<tr[^>]*>([\d\w\S]+)</tr" )
	re_td = re.compile( "<td[^>]*>([a-zA-Z0-9\s\d\w\"\#\=\'\-\.\_\\\/\?\:\(\)\[\]\>\<]*|^\<\/td\>|^\<td )</td>" )
	#page = toolbox.url_get( lookfor_uris[1] ).replace( "\n", "" ).replace( "\r", "" )
	#f = open( 'data/page.cache', 'w' )
	#f.write( page )
	#f.close()
	page = open( 'data/page.cache', 'r' ).read()
	print "\n ### ".join( re_td.findall( page ) )
#	print re_tr.findall( lf.tr.replace( "\n", "" ).replace( "\r", "" ) )
	#print page
	torrentz_eu =	""" http://torrentz.eu/search?q= """	
