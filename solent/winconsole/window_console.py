#
# window_console
#
# // overview
# Pygame wrapper. Provides devices for keystroke and rogue display
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
from solent.console import console_new
from solent.console import e_colpair
from solent.console import e_keycode
from solent.console import keystream_new
from solent.log import log

from solent.exceptions import SolentQuitException

from collections import deque
import os
import pygame

PROFILE_RED_T = ((255, 0, 0), (0, 0, 0))
PROFILE_GREEN_T = ((0, 255, 0), (0, 0, 0))
PROFILE_YELLOW_T = ((255, 255, 0), (0, 0, 0))
PROFILE_BLUE_T = ((0, 0, 255), (0, 0, 0))
PROFILE_PURPLE_T = ((255, 0, 255), (0, 0, 0))
PROFILE_CYAN_T = ((0, 255, 255), (0, 0, 0))
PROFILE_WHITE_T = ((255, 255, 255), (0, 0, 0))
PROFILE_T_RED = ((0, 0, 0), (255, 0, 0))
PROFILE_T_GREEN = ((0, 0, 0), (0, 255, 0))
PROFILE_T_YELLOW = ((0, 0, 0), (255, 255, 0))
PROFILE_WHITE_BLUE = ((255, 255, 255), (255, 255, 128))
PROFILE_WHITE_PURPLE = ((255, 255, 255), (255, 0, 255))
PROFILE_BLACK_CYAN = ((0, 0, 0), (0, 255, 255))
PROFILE_T_WHITE = ((0, 0, 0), (255, 255, 255))

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

def _window_console_translate_key(u):
    if 0 == len(u):
        return None
    if u == u'\r':
        return u'\n'
    return u

class GridDisplay(object):
    def __init__(self, width, height, font):
        self.width = width
        self.height = height
        self.font = font
        #
        self.internal_cgrid = cgrid_new(
            width=width,
            height=height)
        (self.cwidth, self.cheight) = font.size('@')
        #
        dim = (width * self.cwidth, height * self.cheight)
        self.screen = pygame.display.set_mode(dim)
    def update(self, cgrid):
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
            (font_fg, font_bg) = MAP_CONST_COLOURS_TO_CPAIR[spot.cpair]
            label = self.font.render(spot.c, 1, font_fg, font_bg)
            #
            drop_pixels = self.cwidth*int(idx%self.internal_cgrid.width)
            rest_pixels = self.cheight*int(idx/self.internal_cgrid.width)
            self.screen.blit(label, (drop_pixels, rest_pixels))
        pygame.display.flip()
    def coords_from_mousepos(self, xpos, ypos):
        '''
        From the supplied pixel dimensions, return the drop and rest of the
        selected grid reference.
        '''
        rest = int(xpos / self.cwidth)
        drop = int(ypos / self.cheight)
        return (drop, rest)


# --------------------------------------------------------
#   :interface
# --------------------------------------------------------
class WindowConsole:
    def __init__(self, width, height, font):
        self.width = width
        self.height = height
        self.font = font
        #
        self.grid_display = GridDisplay(
            width=width,
            height=height,
            font=font)
        #
        self.keystream = keystream_new(
            cb_async_getc=self.async_getc,
            cb_block_getc=self.block_getc)
        #
        self.event_queue = deque()
        #
        # (drop, rest)
        self.last_lmousedown = None
        self.last_lmouseup = None
        self.last_rmousedown = None
        self.last_rmouseup = None
    def on_close(self):
        pygame.quit()
    def get_last_lmousedown(self):
        return self.last_lmousedown
    def get_last_lmouseup(self):
        return self.last_lmouseup
    def get_last_rmousedown(self):
        return self.last_rmousedown
    def get_last_rmouseup(self):
        return self.last_rmouseup
    def get_grid_display(self):
        return self.grid_display
    def get_keystream(self):
        return self.keystream
    def async_getc(self):
        for itm in pygame.event.get():
            self.event_queue.append(itm)
        # The reason this is a while loop is to get through event characters
        # we don't care about. i.e. it's a different reason for a while loop
        # in the same position in block_getc. (At first glance, it looks
        # trivial to merge them, but it's not)
        while True:
            if not self.event_queue:
                return None
            ev = self.event_queue.popleft()
            if ev.type == pygame.QUIT:
                raise SolentQuitException()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                (xpos, ypos) = ev.pos
                if ev.button == 1:
                    self.last_lmousedown = self.grid_display.coords_from_mousepos(
                        xpos=xpos,
                        ypos=ypos)
                    return e_keycode.lmousedown
                if ev.button == 3:
                    self.last_rmousedown = self.grid_display.coords_from_mousepos(
                        xpos=xpos,
                        ypos=ypos)
                    return e_keycode.rmousedown
            if ev.type == pygame.MOUSEBUTTONUP:
                (xpos, ypos) = ev.pos
                if ev.button == 1:
                    self.last_lmouseup = self.grid_display.coords_from_mousepos(
                        xpos=xpos,
                        ypos=ypos)
                    return e_keycode.lmouseup
                if ev.button == 3:
                    self.last_rmouseup = self.grid_display.coords_from_mousepos(
                        xpos=xpos,
                        ypos=ypos)
                    return e_keycode.rmouseup
            if not ev.type == pygame.KEYDOWN:
                continue
            #
            c = _window_console_translate_key(
                u=ev.unicode)
            return c
    def block_getc(self):
        while True:
            if self.event_queue:
                ev = self.event_queue.popleft()
            else:
                ev = pygame.event.wait()
            #
            if ev.type == pygame.QUIT:
                raise SolentQuitException()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                (xpos, ypos) = ev.pos
                self.last_mousedown = self.grid_display.coords_from_mousepos(
                    xpos=xpos,
                    ypos=ypos)
                return e_keycode.mousedown
            if ev.type == pygame.MOUSEBUTTONUP:
                (xpos, ypos) = ev.pos
                self.last_mouseup = self.grid_display.coords_from_mousepos(
                    xpos=xpos,
                    ypos=ypos)
                return e_keycode.mouseup
            if not ev.type == pygame.KEYDOWN:
                continue
            #
            c = _window_console_translate_key(
                u=ev.unicode)
            return c

DIR_CODE = os.path.realpath(os.path.dirname(__file__))
DIR_FONT = os.sep.join( [DIR_CODE, 'fonts'] )
PATH_TTF_FONT = os.sep.join( [DIR_FONT, 'kongtext', 'kongtext.ttf'] )

def window_console_new(width, height):
    pygame.font.init()
    font = pygame.font.Font(PATH_TTF_FONT, 16)
    window_console = WindowConsole(
        width=width,
        height=height,
        font=font)
    #
    ob = console_new(
        keystream=window_console.get_keystream(),
        grid_display=window_console.get_grid_display(),
        width=width,
        height=height,
        cb_last_lmouseup=window_console.get_last_lmouseup,
        cb_last_lmousedown=window_console.get_last_lmousedown,
        cb_last_rmouseup=window_console.get_last_rmouseup,
        cb_last_rmousedown=window_console.get_last_rmousedown,
        cb_close=window_console.on_close)
    return ob

