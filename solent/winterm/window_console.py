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

from solent.term import cgrid_new
from solent.term import console_new
from solent.term import e_colpair
from solent.term import e_keycode
from solent.term import keystream_new

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
        return e_keycode.newline.value
    if ord(u) == 0x8:
        return e_keycode.backspace.value
    return u

Q_ASYNC_GETC = deque()
def pygame_async_getc():
    global Q_ASYNC_GETC
    for itm in pygame.event.get():
        Q_ASYNC_GETC.append(itm)
    while True:
        if not Q_ASYNC_GETC:
            return None
        ev = Q_ASYNC_GETC.popleft()
        if ev.type == pygame.QUIT:
            raise SolentQuitException()
        if not ev.type == pygame.KEYDOWN:
            continue
        c = _window_console_translate_key(
            u=ev.unicode)
        return c

def pygame_block_getc():
    while True:
        ev = pygame.event.wait()
        #
        if ev.type == pygame.QUIT:
            raise SolentQuitException()
        if not ev.type == pygame.KEYDOWN:
            continue
        #
        c = _window_console_translate_key(
            u=ev.unicode)
        return c

class GridDisplay(object):
    def __init__(self, internal_cgrid, font):
        self.internal_cgrid = internal_cgrid
        self.font = font
        #
        width = internal_cgrid.width
        height = internal_cgrid.height
        #
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


# --------------------------------------------------------
#   :interface
# --------------------------------------------------------
DIR_CODE = os.path.realpath(os.path.dirname(__file__))
DIR_FONT = os.sep.join( [DIR_CODE, 'kongtext-font'] )
PATH_TTF_FONT = os.sep.join( [DIR_FONT, 'kongtext.ttf'] )

CONSOLE = None

def window_console_start(width, height):
    global CONSOLE
    if None != CONSOLE:
        raise Exception('window_console is singleton. (cannot restart)')
    #
    cgrid = cgrid_new(
        width=width,
        height=height)
    pygame.font.init()
    font = pygame.font.Font(PATH_TTF_FONT, 16)
    #
    keystream = keystream_new(
        cb_async_getc=pygame_async_getc,
        cb_block_getc=pygame_block_getc)
    grid_display = GridDisplay(
        internal_cgrid=cgrid,
        font=font)
    CONSOLE = console_new(
        keystream=keystream,
        grid_display=grid_display,
        width=width,
        height=height)
    return CONSOLE

def window_console_end():
    CONSOLE = None
    pygame.quit()

