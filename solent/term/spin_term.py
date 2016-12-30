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
from solent.log import log
from solent.util import uniq

import time

try:
    from solent.winconsole import window_console_new as console_new
except:
    from solent.console import curses_console_new as console_new

KEY_ENTER = 10
KEY_ESC = 27
KEY_a = ord('a')
KEY_b = ord('b')
KEY_c = ord('c')
KEY_d = ord('d')
KEY_e = ord('e')
KEY_f = ord('f')
KEY_g = ord('g')
KEY_h = ord('h')
KEY_i = ord('i')
KEY_j = ord('j')
KEY_k = ord('k')
KEY_l = ord('l')
KEY_m = ord('m')
KEY_n = ord('n')
KEY_o = ord('o')
KEY_p = ord('p')
KEY_q = ord('q')
KEY_r = ord('r')
KEY_s = ord('s')
KEY_t = ord('t')
KEY_u = ord('u')
KEY_v = ord('v')
KEY_w = ord('w')
KEY_x = ord('x')
KEY_y = ord('y')
KEY_z = ord('z')
KEY_A = ord('A')
KEY_B = ord('B')
KEY_C = ord('C')
KEY_D = ord('D')
KEY_E = ord('E')
KEY_F = ord('F')
KEY_G = ord('G')
KEY_H = ord('H')
KEY_I = ord('I')
KEY_J = ord('J')
KEY_K = ord('K')
KEY_L = ord('L')
KEY_M = ord('M')
KEY_N = ord('N')
KEY_O = ord('O')
KEY_P = ord('P')
KEY_Q = ord('Q')
KEY_R = ord('R')
KEY_S = ord('S')
KEY_T = ord('T')
KEY_U = ord('U')
KEY_V = ord('V')
KEY_W = ord('W')
KEY_X = ord('X')
KEY_Y = ord('Y')
KEY_Z = ord('Z')

MODE_NONE = 0
MODE_SELECT = 1
MODE_STANDARD = 2

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
        self.mouse_coords = None
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
            if key == e_keycode.mousedown:
                log('yes %s'%str(self.console.get_last_mousedown()))
                self.mouse_coords = self.console.get_last_mousedown()
            elif key == e_keycode.mouseup:
                pass
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
            if keycode == KEY_ESC:
                self.to_mode_standard()
            if keycode in (KEY_ENTER, KEY_s):
                self.cb_select(
                    drop=self.select_drop,
                    rest=self.select_rest)
                self.to_mode_standard()
            else:
                # we let the user navigate the cursor using arrow keys, vi
                # keys, gollop keys.
                b_moved = False
                # standard navigation
                if keycode in (KEY_q, KEY_a, KEY_z, KEY_y, KEY_h, KEY_b):
                    if self.select_rest > 0:
                        self.select_rest -= 1
                    b_moved = True
                if keycode in (KEY_e, KEY_d, KEY_c, KEY_u, KEY_l, KEY_n):
                    if self.select_rest < self.width-1:
                        self.select_rest += 1
                    b_moved = True
                if keycode in (KEY_q, KEY_w, KEY_e, KEY_y, KEY_k, KEY_u):
                    if self.select_drop > 0:
                        self.select_drop -= 1
                    b_moved = True
                if keycode in (KEY_z, KEY_x, KEY_c, KEY_b, KEY_j, KEY_n):
                    if self.select_drop < self.height-1:
                        self.select_drop += 1
                    b_moved = True
                # shift navigation
                if keycode in (KEY_Q, KEY_A, KEY_Z, KEY_Y, KEY_H, KEY_B):
                    self.select_rest = 0
                    b_moved = True
                if keycode in (KEY_E, KEY_D, KEY_C, KEY_U, KEY_L, KEY_N):
                    self.select_rest = self.width-1
                    b_moved = True
                if keycode in (KEY_Q, KEY_W, KEY_E, KEY_Y, KEY_K, KEY_U):
                    self.select_drop = 0
                    b_moved = True
                if keycode in (KEY_Z, KEY_X, KEY_C, KEY_B, KEY_J, KEY_N):
                    self.select_drop = self.height-1
                    b_moved = True
                #
                if b_moved:
                    self.select_cursor_on = True
                    self.select_cursor_t100 = time.time() * 100
        elif self.mode == MODE_STANDARD:
            if keycode == KEY_ESC:
                self.to_mode_select()
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
    '''
    ob = SpinTerm(
        cb_keycode=cb_keycode,
        cb_select=cb_select)
    return ob

