#
# curses_console
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

from .cgrid import cgrid_new
from .console import console_new
from .enumerations import e_colpair
from .enumerations import e_keycode
from .keystream import keystream_new

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

def _curses_translate_key(k):
    if k in (127, curses.KEY_BACKSPACE, curses.KEY_DC):
        k = 0x8
    c = chr(k)
    return c

Q_ASYNC_GETC = deque()
def curses_async_getc():
    '''
    xxx this doesn't handle escaped characters very well at the moment. could
    create an issue to get that fixed.
    '''
    global STDSCR
    global Q_ASYNC_GETC
    #
    STDSCR.nodelay(1)
    try:
        c = STDSCR.getch()
        while c != -1:
            Q_ASYNC_GETC.append(c)
            c = STDSCR.getch()
    finally:
        STDSCR.nodelay(0)
    #
    if Q_ASYNC_GETC:
        return _curses_translate_key(
            k=Q_ASYNC_GETC.popleft())

def curses_block_getc():
    global STDSCR
    k = STDSCR.getch()
    if None == k:
        return None
    if k < 0 or k >= 256:
        return None
    return _curses_translate_key(
        k=k)

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

MAP_CONST_COLOURS_TO_CPAIR = { e_colpair.red_t: PROFILE_RED_T
                             , e_colpair.green_t: PROFILE_GREEN_T
                             , e_colpair.yellow_t: PROFILE_YELLOW_T
                             , e_colpair.blue_t: PROFILE_BLUE_T
                             , e_colpair.purple_t: PROFILE_PURPLE_T
                             , e_colpair.cyan_t: PROFILE_CYAN_T
                             , e_colpair.white_t: PROFILE_WHITE_T
                             , e_colpair.t_red: PROFILE_RED_T
                             , e_colpair.t_green: PROFILE_T_GREEN
                             , e_colpair.t_yellow: PROFILE_T_YELLOW
                             , e_colpair.white_blue: PROFILE_WHITE_BLUE
                             , e_colpair.white_purple: PROFILE_WHITE_PURPLE
                             , e_colpair.black_cyan: PROFILE_BLACK_CYAN
                             , e_colpair.t_white: PROFILE_T_WHITE
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
        cb_async_getc=curses_async_getc,
        cb_block_getc=curses_block_getc)
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
    CONSOLE = console_new(
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

