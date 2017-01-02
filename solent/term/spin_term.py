#
# spin_term
#
# // overview
# This provides an idea of a 'standard' terminal that can be used in front of
# solent apps. Note that it is not the same thing as a console. The terminal
# acts as a layer similar to a TTY that sits between a system and a console.
# It provides features such as gollop-selection (press escape and use q-c to
# navigate around, and s to select).
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

from solent.console import cgrid_new
from solent.console import e_colpair
from solent.console import e_keycode
from solent.console import key
from solent.log import log
from solent.util import uniq

import time

try:
    from solent.winconsole import window_console_new as console_new
except:
    from solent.console import curses_console_new as console_new

MODE_NONE = 0
MODE_SELECT = 1
MODE_STANDARD = 2

MOUSE_EVENTS = (
    e_keycode.lmousedown.value,
    e_keycode.lmouseup.value,
    e_keycode.rmousedown.value,
    e_keycode.rmouseup.value)

class SpinTerm:
    def __init__(self, cb_keycode, cb_select):
        self.cb_keycode = cb_keycode
        self.cb_select = cb_select
        #
        self.width = None
        self.height = None
        self.cgrid = None
        self.mode = MODE_NONE
        self.console = None
        self.select_cursor_on = True
        self.select_cursor_t100 = time.time() * 100
        self.select_drop = 0
        self.select_rest = 0
        self.select_cgrid = None
        #
        self.lmousedown_coords = None
    #
    def close(self):
        if None != self.console:
            self.console.close()
    def at_turn(self, activity):
        if self.mode == MODE_NONE:
            return
        #
        key = self.console.async_getc()
        if key:
            activity.mark(
                l=self,
                s='received keystroke %s'%key)
            if key == e_keycode.lmousedown:
                keycode = e_keycode.lmousedown.value
                self.lmousedown_coords = self.console.get_last_lmousedown()
            elif key == e_keycode.lmouseup:
                keycode = e_keycode.lmouseup.value
                self.lmouseup_coords = self.console.get_last_lmouseup()
            elif key == e_keycode.rmousedown:
                keycode = e_keycode.rmousedown.value
                self.rmousedown_coords = self.console.get_last_rmousedown()
            elif key == e_keycode.rmouseup:
                keycode = e_keycode.rmouseup.value
                self.rmouseup_coords = self.console.get_last_rmouseup()
            else:
                keycode = ord(key)
            self.accept_key(
                keycode=keycode)
        #
        self.refresh_console()
    #
    def open_console(self, width, height):
        self.width = width
        self.height = height
        self.cgrid = cgrid_new(
            width=width,
            height=height)
        self.select_cgrid = cgrid_new(
            width=width,
            height=height)
        self.console = console_new(
            width=width,
            height=height)
        self.mode = MODE_STANDARD
    def close_console(self):
        if not self.console:
            return
        self.console.close()
        self.mode = MODE_NONE
        self.select_drop = 0
        self.select_rest = 0
    def to_mode_standard(self):
        if None == self.console:
            raise Exception("No console open")
        self.mode = MODE_STANDARD
    def to_mode_select(self):
        if None == self.console:
            raise Exception("No console open")
        self.mode = MODE_SELECT
        self.select_cursor_on = True
        self.select_cursor_t100 = time.time() * 100
    def clear(self):
        self.cgrid.clear()
    def write(self, drop, rest, s, cpair):
        self.cgrid.put(
            drop=drop,
            rest=rest,
            s=s,
            cpair=cpair)
    def accept_key(self, keycode):
        '''
        By making this an exposed command, we can allow the console to be used
        as a display with input coming from elsewhere.
        '''
        if self.mode == MODE_SELECT:
            if keycode == key('esc'):
                self.to_mode_standard()
            if keycode in (key('newline'), key('s')):
                self.cb_select(
                    drop=self.select_drop,
                    rest=self.select_rest)
                self.to_mode_standard()
            else:
                # we let the user navigate the cursor using arrow keys, vi
                # keys, gollop keys.
                b_moved = False
                # standard navigation
                if keycode in (key('q'), key('a'), key('z'), key('y'), key('h'), key('b')):
                    if self.select_rest > 0:
                        self.select_rest -= 1
                    b_moved = True
                if keycode in (key('e'), key('d'), key('c'), key('u'), key('l'), key('n')):
                    if self.select_rest < self.width-1:
                        self.select_rest += 1
                    b_moved = True
                if keycode in (key('q'), key('w'), key('e'), key('y'), key('k'), key('u')):
                    if self.select_drop > 0:
                        self.select_drop -= 1
                    b_moved = True
                if keycode in (key('z'), key('x'), key('c'), key('b'), key('j'), key('n')):
                    if self.select_drop < self.height-1:
                        self.select_drop += 1
                    b_moved = True
                # shift navigation
                if keycode in (key('Q'), key('A'), key('Z'), key('Y'), key('H'), key('B')):
                    self.select_rest = 0
                    b_moved = True
                if keycode in (key('E'), key('D'), key('C'), key('U'), key('L'), key('N')):
                    self.select_rest = self.width-1
                    b_moved = True
                if keycode in (key('Q'), key('W'), key('E'), key('Y'), key('K'), key('U')):
                    self.select_drop = 0
                    b_moved = True
                if keycode in (key('Z'), key('X'), key('C'), key('B'), key('J'), key('N')):
                    self.select_drop = self.height-1
                    b_moved = True
                #
                if b_moved:
                    self.select_cursor_on = True
                    self.select_cursor_t100 = time.time() * 100
        elif self.mode == MODE_STANDARD:
            if keycode == key('esc'):
                self.to_mode_select()
            else:
                if keycode == e_keycode.lmouseup.value:
                    # We check to see that the coords were the same as
                    # when the mouse was depressed. If they weren't, this
                    # usually implies the user has rethought their
                    # decision, and we abort. From memory, this is how FTL
                    # works, and it's super-useful.
                    (ddrop, drest) = self.lmousedown_coords
                    (udrop, urest) = self.lmouseup_coords
                    if (ddrop, drest) == (udrop, urest):
                        self.cb_select(
                            drop=udrop,
                            rest=urest)
                elif keycode in MOUSE_EVENTS:
                    pass
                else:
                    # we pass the keystroke back in a callback
                    self.cb_keycode(
                        keycode=keycode)
    def refresh_console(self):
        if self.mode == MODE_NONE:
            pass
        elif self.mode == MODE_SELECT:
            # cursor flipping
            t100 = time.time() * 100
            if t100 - self.select_cursor_t100 > 53:
                self.select_cursor_t100 = t100
                if self.select_cursor_on:
                    self.select_cursor_on = False
                else:
                    self.select_cursor_on = True
            # cursor display
            self.select_cgrid.blit(
                src_cgrid=self.cgrid)
            if self.select_cursor_on:
                self.select_cgrid.put(
                    drop=self.select_drop,
                    rest=self.select_rest,
                    s='@',
                    cpair=e_colpair.red_t)
            self.console.screen_update(
                cgrid=self.select_cgrid)
        elif self.mode == MODE_STANDARD:
            self.console.screen_update(
                cgrid=self.cgrid)

def spin_term_new(cb_keycode, cb_select):
    '''
    cb_keycode(keycode)
    cb_select(drop, rest)
        # We are avoiding more complex forms of selection (e.g. left and
        # right mouse) because we want the interface to be viable as a
        # touch interface. We will probably need to support left dragging
        # later on.
    '''
    ob = SpinTerm(
        cb_keycode=cb_keycode,
        cb_select=cb_select)
    return ob

