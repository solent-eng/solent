#
# curses console
#
# // license
# Copyright 2016, Free Software Foundation.
#
# This file is part of Solent.
#
# Solent is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# Solent is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# Solent. If not, see <http://www.gnu.org/licenses/>.

from solent import solent_cpair
from solent import solent_keycode
from solent.console import cgrid_new
from solent.console import iconsole_new
from solent.console import keystream_new

from collections import deque
import atexit
import curses
import os
import select
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
    curses.init_pair(PROFILE_GREY       , curses.COLOR_WHITE    , -1)
    curses.init_pair(PROFILE_WHITE      , curses.COLOR_WHITE    , -1)
    curses.init_pair(PROFILE_RED        , curses.COLOR_RED      , -1)
    curses.init_pair(PROFILE_VERMILION  , curses.COLOR_RED      , -1)
    curses.init_pair(PROFILE_ORANGE     , curses.COLOR_RED      , -1)
    curses.init_pair(PROFILE_AMBER      , curses.COLOR_YELLOW   , -1)
    curses.init_pair(PROFILE_YELLOW     , curses.COLOR_YELLOW   , -1)
    curses.init_pair(PROFILE_CHARTREUSE , curses.COLOR_GREEN    , -1)
    curses.init_pair(PROFILE_GREEN      , curses.COLOR_GREEN    , -1)
    curses.init_pair(PROFILE_TEAL       , curses.COLOR_CYAN     , -1)
    curses.init_pair(PROFILE_BLUE       , curses.COLOR_BLUE     , -1)
    curses.init_pair(PROFILE_VIOLET     , curses.COLOR_MAGENTA  , -1)
    curses.init_pair(PROFILE_PURPLE     , curses.COLOR_MAGENTA  , -1)
    curses.init_pair(PROFILE_MAGENTA    , curses.COLOR_MAGENTA  , -1)
    curses.init_pair(PROFILE_BLACK_INFO , curses.COLOR_BLACK    , curses.COLOR_WHITE)
    curses.init_pair(PROFILE_ALARM,       curses.COLOR_RED      , curses.COLOR_WHITE)

def screen_curses_exit():
    global STDSCR
    STDSCR.keypad(0)
    curses.echo()
    curses.nocbreak()
    curses.endwin()

def _sanitise_key(k):
    if k in (127, curses.KEY_BACKSPACE, curses.KEY_DC):
        k = solent_keycode('backspace')
    return k

Q_ASYNC_GET_KEYCODE = deque()
def curses_async_get_keycode():
    '''
    xxx this doesn't handle escaped characters very well at the moment. could
    create an issue to get that fixed.
    '''
    global STDSCR
    global Q_ASYNC_GET_KEYCODE
    #
    STDSCR.nodelay(1)
    try:
        c = STDSCR.getch()
        while c != -1:
            Q_ASYNC_GET_KEYCODE.append(c)
            c = STDSCR.getch()
    finally:
        STDSCR.nodelay(0)
    #
    if Q_ASYNC_GET_KEYCODE:
        k = _sanitise_key(
            k=Q_ASYNC_GET_KEYCODE.popleft())
        return k

def curses_block_get_keycode():
    global Q_ASYNC_GET_KEYCODE
    if Q_ASYNC_GET_KEYCODE:
        k = _sanitise_key(
            k=Q_ASYNC_GET_KEYCODE.popleft())
        return k
    #
    global STDSCR
    k = STDSCR.getch()
    if None == k:
        return None
    if k < 0x00 or k > 0xff:
        return None
    k = _sanitise_key(k)
    return k

#
# These are not the names of colours. Rather, they are the names of colour
# profiles, each of represents attributes. Here, we will have foreground and
# background. But you could potentially have underling and blinking and that
# sort of thing as well.
PROFILE_GREY = 0
PROFILE_WHITE = 1
PROFILE_RED = 2
PROFILE_VERMILION = 3
PROFILE_ORANGE = 4
PROFILE_AMBER = 5
PROFILE_YELLOW = 6
PROFILE_CHARTREUSE = 7
PROFILE_GREEN = 8
PROFILE_TEAL = 9
PROFILE_BLUE = 10
PROFILE_VIOLET = 11
PROFILE_PURPLE = 12
PROFILE_MAGENTA = 13
PROFILE_BLACK_INFO = 14
PROFILE_ALARM = 15

MAP_CONST_COLOURS_TO_CPAIR = { solent_cpair('grey'): PROFILE_GREY
                             , solent_cpair('white'): PROFILE_WHITE
                             , solent_cpair('red'): PROFILE_RED
                             , solent_cpair('vermilion'): PROFILE_VERMILION
                             , solent_cpair('orange'): PROFILE_ORANGE
                             , solent_cpair('amber'): PROFILE_AMBER
                             , solent_cpair('yellow'): PROFILE_YELLOW
                             , solent_cpair('chartreuse'): PROFILE_CHARTREUSE
                             , solent_cpair('green'): PROFILE_GREEN
                             , solent_cpair('teal'): PROFILE_TEAL
                             , solent_cpair('blue'): PROFILE_BLUE
                             , solent_cpair('violet'): PROFILE_VIOLET
                             , solent_cpair('purple'): PROFILE_PURPLE
                             , solent_cpair('magenta'): PROFILE_MAGENTA
                             , solent_cpair('black_info'): PROFILE_BLACK_INFO
                             , solent_cpair('alarm'): PROFILE_ALARM
                             }

def get_curses_colour_enum_closest_to_cpair(cpair):
    if cpair in MAP_CONST_COLOURS_TO_CPAIR:
        return curses.color_pair(MAP_CONST_COLOURS_TO_CPAIR[cpair])|curses.A_BOLD
    else:
        choice_cpair = None
        for (avail_cpair, curses_pair_id) in MAP_CONST_COLOURS_TO_CPAIR.items():
            if choice_cpair == None:
                choice_cpair = avail_cpair
                continue
            # Locate the closest to the desired cpair that is not larger than
            # it
            if avail_cpair > cpair:
                continue
            elif avail_cpair > choice_cpair:
                choice_cpair = avail_cpair
        return avail_cpair|curses.A_BOLD

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
                pair = get_curses_colour_enum_closest_to_cpair(
                    cpair=spot.cpair)
                STDSCR.addstr(
                    int(idx/self.internal_cgrid.width),
                    int(idx%self.internal_cgrid.width),
                    spot.c,
                    pair)
            # consistent cursor position
            spot = self.internal_cgrid.spots[-1]
            pair = get_curses_colour_enum_closest_to_cpair(
                cpair=spot.cpair)
            STDSCR.addstr(
                self.internal_cgrid.height-1,
                self.internal_cgrid.width-1,
                spot.c,
                pair)
            #
            STDSCR.refresh()
        except:
            # xxx
            raise
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

def curses_console_new(width, height):
    global CONSOLE
    if None != CONSOLE:
        raise Exception('curses console is singleton. (cannot run more than one)')
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
        cb_async_get_keycode=curses_async_get_keycode,
        cb_block_get_keycode=curses_block_get_keycode)
    grid_display = GridDisplay(
        internal_cgrid=cgrid)
    #
    # Emphasis: see note about regarding keystream: ordering is significant.
    screen_curses_init()
    #
    def on_close():
        screen_curses_exit()
        #
        global CONSOLE
        CONSOLE = None
    CONSOLE = iconsole_new(
        keystream=keystream,
        grid_display=grid_display,
        width=width,
        height=height,
        cb_last_lmouseup=lambda: None,
        cb_last_lmousedown=lambda: None,
        cb_last_rmouseup=lambda: None,
        cb_last_rmousedown=lambda: None,
        cb_close=on_close)
    return CONSOLE

