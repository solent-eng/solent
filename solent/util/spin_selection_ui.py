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
#
# // overview
# This provides an idea of a 'standard' terminal that can be used in front of
# solent apps. The key thing it offers of a console is selection:
# * Via mouse, in consoles that support this
# * Via gollop-style selection (press escape and use q-c to navigate around,
# and s to select)
#
# For fast business utilities, it is probably more convenient to start with
# an instance of this span than a console.
#

from solent import solent_cpair
from solent import solent_keycode
from solent import uniq
from solent.console import Cgrid
from solent.console import Console
from solent.log import log

import time

MODE_NONE = 0
MODE_SELECT = 1
MODE_STANDARD = 2

MOUSE_EVENTS = (
    solent_keycode('lmousedown'),
    solent_keycode('lmouseup'),
    solent_keycode('rmousedown'),
    solent_keycode('rmouseup'))

class CsSeluiKeycode:
    def __init__(self):
        self.keycode = None

class CsSeluiLselect:
    def __init__(self):
        self.drop = None
        self.rest = None
        self.c = None
        self.cpair = None

class SpinSelectionUi:
    def __init__(self, spin_h, engine, console_type, cb_selui_keycode, cb_selui_lselect):
        self.spin_h = spin_h
        self.engine = engine
        self.console_type = console_type
        self.cb_selui_keycode = cb_selui_keycode
        self.cb_selui_lselect = cb_selui_lselect
        #
        self.cs_selui_keycode = CsSeluiKeycode()
        self.cs_selui_lselect = CsSeluiLselect()
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
    def eng_turn(self, activity):
        if self.mode == MODE_NONE:
            return
        #
        keycode = self.console.async_get_keycode()
        if keycode:
            activity.mark(
                l=self,
                s='received keystroke %s'%keycode)
            if keycode == solent_keycode('lmousedown'):
                self.lmousedown_coords = self.console.get_last_lmousedown()
            elif keycode == solent_keycode('lmouseup'):
                self.lmouseup_coords = self.console.get_last_lmouseup()
            elif keycode == solent_keycode('rmousedown'):
                self.rmousedown_coords = self.console.get_last_rmousedown()
            elif keycode == solent_keycode('rmouseup'):
                self.rmouseup_coords = self.console.get_last_rmouseup()
            self.accept_key(
                keycode=keycode)
        #
        self.refresh_console()
    def eng_close(self):
        if None != self.console:
            self.console.close()
    #
    def open_console(self, width, height):
        self.width = width
        self.height = height
        self.cgrid = Cgrid(
            width=width,
            height=height)
        self.select_cgrid = Cgrid(
            width=width,
            height=height)
        self.console = Console(
            console_type=self.console_type,
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
    def scroll(self):
        self.cgrid.scroll()
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
            if keycode == solent_keycode('esc'):
                self.to_mode_standard()
            elif keycode in (solent_keycode('newline'), solent_keycode('s')):
                (c, cpair) = self.cgrid.get(
                    drop=self.select_drop,
                    rest=self.select_rest)
                self._call_selui_lselect(
                    drop=self.select_drop,
                    rest=self.select_rest,
                    c=c,
                    cpair=cpair)
                self.to_mode_standard()
            else:
                # we let the user navigate the cursor using arrow keys, vi
                # keys, gollop keys.
                b_moved = False
                # standard navigation
                if keycode in (solent_keycode('q'), solent_keycode('a'), solent_keycode('z'), solent_keycode('y'), solent_keycode('h'), solent_keycode('b')):
                    if self.select_rest > 0:
                        self.select_rest -= 1
                    b_moved = True
                if keycode in (solent_keycode('e'), solent_keycode('d'), solent_keycode('c'), solent_keycode('u'), solent_keycode('l'), solent_keycode('n')):
                    if self.select_rest < self.width-1:
                        self.select_rest += 1
                    b_moved = True
                if keycode in (solent_keycode('q'), solent_keycode('w'), solent_keycode('e'), solent_keycode('y'), solent_keycode('k'), solent_keycode('u')):
                    if self.select_drop > 0:
                        self.select_drop -= 1
                    b_moved = True
                if keycode in (solent_keycode('z'), solent_keycode('x'), solent_keycode('c'), solent_keycode('b'), solent_keycode('j'), solent_keycode('n')):
                    if self.select_drop < self.height-1:
                        self.select_drop += 1
                    b_moved = True
                # shift navigation
                if keycode in (solent_keycode('Q'), solent_keycode('A'), solent_keycode('Z'), solent_keycode('Y'), solent_keycode('H'), solent_keycode('B')):
                    self.select_rest = 0
                    b_moved = True
                if keycode in (solent_keycode('E'), solent_keycode('D'), solent_keycode('C'), solent_keycode('U'), solent_keycode('L'), solent_keycode('N')):
                    self.select_rest = self.width-1
                    b_moved = True
                if keycode in (solent_keycode('Q'), solent_keycode('W'), solent_keycode('E'), solent_keycode('Y'), solent_keycode('K'), solent_keycode('U')):
                    self.select_drop = 0
                    b_moved = True
                if keycode in (solent_keycode('Z'), solent_keycode('X'), solent_keycode('C'), solent_keycode('B'), solent_keycode('J'), solent_keycode('N')):
                    self.select_drop = self.height-1
                    b_moved = True
                #
                if b_moved:
                    self.select_cursor_on = True
                    self.select_cursor_t100 = time.time() * 100
        elif self.mode == MODE_STANDARD:
            if keycode == solent_keycode('esc'):
                self.to_mode_select()
            else:
                if keycode == solent_keycode('lmouseup'):
                    # We check to see that the coords were the same as
                    # when the mouse was depressed. If they weren't, this
                    # usually implies the user has rethought their
                    # decision, and we abort. From memory, this is how FTL
                    # works, and it's super-useful.
                    (ddrop, drest) = self.lmousedown_coords
                    (udrop, urest) = self.lmouseup_coords
                    if (ddrop, drest) == (udrop, urest):
                        (c, cpair) = self.cgrid.get(
                            drop=udrop,
                            rest=urest)
                        self._call_selui_lselect(
                            drop=udrop,
                            rest=urest,
                            c=c,
                            cpair=cpair)
                elif keycode in MOUSE_EVENTS:
                    pass
                else:
                    # we pass the keystroke back in a callback
                    self._call_selui_keycode(
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
                    cpair=solent_cpair('red'))
            self.console.screen_update(
                cgrid=self.select_cgrid)
        elif self.mode == MODE_STANDARD:
            self.console.screen_update(
                cgrid=self.cgrid)
    #
    def _call_selui_keycode(self, keycode):
        self.cs_selui_keycode.keycode = keycode
        self.cb_selui_keycode(
            cs_selui_keycode=self.cs_selui_keycode)
    def _call_selui_lselect(self, drop, rest, c, cpair):
        self.cs_selui_lselect.drop = drop
        self.cs_selui_lselect.rest = rest
        self.cs_selui_lselect.c = c
        self.cs_selui_lselect.cpair = cpair
        self.cb_selui_lselect(
            cs_selui_lselect=self.cs_selui_lselect)

