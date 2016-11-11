from .console import console_new
from .cgrid import cgrid_new
from .keystream import keystream_new

from solent.client.constants import *

from select import select
import atexit
import curses
import os
import sys
import termios
import time
import traceback
import tty

STDSCR = None

def screen_curses_init():
    #
    # number of milliseconds to wait after reading an escape character, to
    # distinguish between an individual escape character entered on the
    # keyboard from escape sequences sent by cursor and function keys (see
    # curses(3X).
    os.putenv("ESCDELAY", "0") # was 25
    #
    global STDSCR
    STDSCR = curses.initscr()
    #STDSCR.nodelay(1)
    curses.noecho()
    curses.cbreak()
    #
    if not curses.has_colors():
        raise Exception("Need colour support to run.")
    curses.raw()
    #
    curses.start_color()
    #
    # This is what allows us to use -1 for default when we initialise
    # the pairs
    curses.use_default_colors()
    #
    curses.init_pair(PROFILE_RED_T, curses.COLOR_RED, -1)
    curses.init_pair(PROFILE_GREEN_T, curses.COLOR_GREEN, -1)
    curses.init_pair(PROFILE_YELLOW_T, curses.COLOR_YELLOW, -1)
    curses.init_pair(PROFILE_BLUE_T, curses.COLOR_BLUE, -1)
    curses.init_pair(PROFILE_PURPLE_T, curses.COLOR_MAGENTA, -1)
    curses.init_pair(PROFILE_CYAN_T, curses.COLOR_CYAN, -1)
    curses.init_pair(PROFILE_WHITE_T, curses.COLOR_WHITE, -1)
    curses.init_pair(PROFILE_T_RED, -1, curses.COLOR_RED)
    curses.init_pair(PROFILE_T_GREEN, -1, curses.COLOR_GREEN)
    curses.init_pair(PROFILE_T_YELLOW, -1, curses.COLOR_YELLOW)
    curses.init_pair(PROFILE_WHITE_BLUE, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(PROFILE_WHITE_PURPLE, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
    curses.init_pair(PROFILE_BLACK_CYAN, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(PROFILE_T_WHITE, -1, curses.COLOR_WHITE)

def screen_curses_exit():
    global STDSCR
    STDSCR.keypad(0)
    curses.echo()
    curses.nocbreak()
    curses.endwin()

def curses_getc():
    global STDSCR
    k = STDSCR.getch()
    if None == k:
        return None
    if k < 0 or k >= 256:
        return None
    c = chr(k)
    return c

#
# These are not the names of colours. Rather, they are the names of colour
# profiles, each of represents attributes. Here, we will have foreground and
# background. But you could potentially have underling and blinking and that
# sort of thing as well.
PROFILE_RED_T = 1
PROFILE_GREEN_T = 2
PROFILE_YELLOW_T = 3
PROFILE_BLUE_T = 4
PROFILE_PURPLE_T = 5
PROFILE_CYAN_T = 6
PROFILE_WHITE_T = 7
PROFILE_T_RED = 11
PROFILE_T_GREEN = 12
PROFILE_T_YELLOW = 13
PROFILE_WHITE_BLUE = 14
PROFILE_WHITE_PURPLE = 15
PROFILE_BLACK_CYAN = 16
PROFILE_T_WHITE = 17

MAP_CONST_COLOURS_TO_CPAIR = { SOL_CPAIR_RED_T: PROFILE_RED_T
                             , SOL_CPAIR_GREEN_T: PROFILE_GREEN_T
                             , SOL_CPAIR_YELLOW_T: PROFILE_YELLOW_T
                             , SOL_CPAIR_BLUE_T: PROFILE_BLUE_T
                             , SOL_CPAIR_PURPLE_T: PROFILE_PURPLE_T
                             , SOL_CPAIR_CYAN_T: PROFILE_CYAN_T
                             , SOL_CPAIR_WHITE_T: PROFILE_WHITE_T
                             , SOL_CPAIR_T_RED: PROFILE_RED_T
                             , SOL_CPAIR_T_GREEN: PROFILE_T_GREEN
                             , SOL_CPAIR_T_YELLOW: PROFILE_T_YELLOW
                             , SOL_CPAIR_WHITE_BLUE: PROFILE_WHITE_BLUE
                             , SOL_CPAIR_WHITE_PURPLE: PROFILE_WHITE_PURPLE
                             , SOL_CPAIR_BLACK_CYAN: PROFILE_BLACK_CYAN
                             , SOL_CPAIR_T_WHITE: PROFILE_T_WHITE
                             }

class GridDisplay(object):
    def __init__(self, internal_cgrid):
        # internal representation of what is on the screen at the moment.
        self.internal_cgrid = internal_cgrid
    def update(self, cgrid):
        '''I have implemented a simple exception catch here. If the user
        resizes their window, then curses can have trouble displaying. In this
        situation, I just diappear the error. This gives then an opportunity
        to fix the resizing situation without distroying their game.
        '''
        try:
            global STDSCR
            cur_dim = (self.internal_cgrid.width, self.internal_cgrid.height)
            new_dim = (cgrid.width, cgrid.height)
            if cur_dim != new_dim:
                self.internal_cgrid.set_dimensions(
                    width=cgrid.width,
                    height=cgrid.height)
            updates = []
            o_spots = self.internal_cgrid.spots
            n_spots = cgrid.spots
            for idx, (o_spot, n_spot) in enumerate(zip(o_spots, n_spots)):
                if not o_spot.compare(n_spot):
                    updates.append(idx)
                    o_spot.mimic(n_spot)
            for idx in updates:
                spot = self.internal_cgrid.spots[idx]
                pair = curses.color_pair(MAP_CONST_COLOURS_TO_CPAIR[spot.cpair])
                STDSCR.addstr(
                    int(idx/self.internal_cgrid.width),
                    int(idx%self.internal_cgrid.width),
                    spot.c,
                    pair)
            # consistent cursor position
            spot = self.internal_cgrid.spots[-1]
            pair = curses.color_pair(MAP_CONST_COLOURS_TO_CPAIR[spot.cpair])
            STDSCR.addstr(
                self.internal_cgrid.height-1,
                self.internal_cgrid.width-1,
                spot.c,
                pair)
            #
            STDSCR.refresh()
        except:
            self.internal_cgrid.clear()
            try:
                STDSCR.clear()
                STDSCR.addstr(0, 0, 'window too small')
                STDSCR.refresh()
                STDSCR.clear()
            except:
                pass
            time.sleep(0.1)


# --------------------------------------------------------
#   :interface
# --------------------------------------------------------
CONSOLE = None

def curses_console_start(width, height):
    global CONSOLE
    if None != CONSOLE:
        raise Exception('curses console is singleton. (cannot restart)')
    cgrid = cgrid_new(
        width=width,
        height=height)
    #
    # Weird: it looks like you need to declare the keystroke source before
    # you do screen init. These kind of bizarre ordering problems are the
    # reason that it's good to have this stuff wrapped up in a library:
    # solve the nasty problem, and then facade things so your user doesn't
    # have to think about it.
    keystream = keystream_new(
        fn_getc=curses_getc)
    grid_display = GridDisplay(
        internal_cgrid=cgrid)
    #
    # Emphasis: see note about regarding keystream: ordering is significant.
    screen_curses_init()
    #
    CONSOLE = console_new(
        keystream=keystream,
        grid_display=grid_display,
        width=width,
        height=height)
    return CONSOLE

def curses_console_end():
    screen_curses_exit()
    #
    global CONSOLE
    CONSOLE = None

