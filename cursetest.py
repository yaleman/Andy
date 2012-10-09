#!/usr/bin/python

import curses
#import curses.wrapper

# init the screen
stdscr = curses.initscr()

# turn off screen echo of keys
#curses.noecho()

# turn off the need for a CR-LF before processing keypresses
#curses.cbreak()

# turn on special key processing
#stdscr.keypad( 1 )

begin_x = 20
begin_y = 7
height = 5
width = 40
win = curses.newwin( height, width, begin_y, begin_x )

pad = curses.newpad( 100, 100 )
for y in xrange( 0, 100 ):
	for x in xrange( 0, 100 ):
		try: 
			pad.addch( y, x, ord('a') + x*x+y*x % 26 )
		except curses.error:
			pass

pad.refresh( 0,0, 5,5, 20, 75 )

for i in range( 1, 100000 ):
	n = i

# return your terminal to normal mode
curses.nocbreak()
stdscr.keypad( 0 )
curses.echo()
curses.endwin()

#def dostuff( e ):
#	print "Hi!"

#curses.wrapper( dostuff )
