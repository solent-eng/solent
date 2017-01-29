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

from solent import solent_cpair
from solent import solent_keycode
from solent import dget_static
from solent.console import cgrid_new
from solent.console import iconsole_new
from solent.console import keystream_new
from solent.log import log

from solent.exceptions import SolentQuitException

from collections import deque
import os
import pygame

KEY_REPEAT_DELAY = 170
KEY_REPEAT_INTERVAL = 180

def rgb(s):
    return (
        eval('0x%s'%(s[:2])),
        eval('0x%s'%(s[2:4])),
        eval('0x%s'%(s[4:6])))

# foreground triplet on background triplet
PROFILE_GREY        = (rgb('aaaaaa')    , (0, 0, 0))
PROFILE_WHITE       = ((255, 255, 255)  , (0, 0, 0))
PROFILE_RED         = ((255, 0, 0)      , (0, 0, 0))
PROFILE_VERMILION   = ((255, 70, 0)     , (0, 0, 0))
PROFILE_ORANGE      = ((255, 118, 0)    , (0, 0, 0))
PROFILE_AMBER       = ((255, 172, 0)    , (0, 0, 0)) 
PROFILE_YELLOW      = ((255, 255, 0)    , (0, 0, 0))
PROFILE_CHARTREUSE  = (rgb('7FFF00')    , (0, 0, 0))
PROFILE_GREEN       = ((0, 255, 0)      , (0, 0, 0))
PROFILE_TEAL        = ((0, 128, 128)    , (0, 0, 0))
PROFILE_BLUE        = ((0, 0, 255)      , (0, 0, 0))
PROFILE_VIOLET      = ((128, 0, 255)    , (0, 0, 0))
PROFILE_PURPLE      = ((255, 0, 255)    , (0, 0, 0))
PROFILE_MAGENTA     = ((255, 127, 255)  , (0, 0, 0))

PROFILE_BLACK_INFO  = ((0, 0, 0)        , (255, 255, 255))
PROFILE_GREY_INFO   = ((0, 0, 0)        , (127, 127, 127))

PROFILE_GREEN_INFO  = ((0, 255, 0)      , (255, 255, 255))

PROFILE_ALARM       = ((255, 64, 0)     , (0, 255, 255))

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
                             , solent_cpair('grey_info'): PROFILE_GREY_INFO
                             , solent_cpair('green_info'): PROFILE_GREEN_INFO
                             , solent_cpair('alarm'): PROFILE_ALARM
                             }

def _sanitise_input(u):
    if 0 == len(u):
        return None
    first_byte = u.encode('latin-1')[0]
    if first_byte == 0x0d:
        return 0x0a
    return first_byte

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

class PygameConsole:
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
            cb_async_get_keycode=self.async_get_keycode,
            cb_block_get_keycode=self.block_get_keycode)
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
    def async_get_keycode(self):
        for itm in pygame.event.get():
            self.event_queue.append(itm)
        # The reason this is a while loop is to get through event characters
        # we don't care about. i.e. it's a different reason for a while loop
        # in the same position in block_get_keycode. (At first glance, it
        # looks trivial to merge them, but it's not)
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
                    return solent_keycode('lmousedown')
                if ev.button == 3:
                    self.last_rmousedown = self.grid_display.coords_from_mousepos(
                        xpos=xpos,
                        ypos=ypos)
                    return solent_keycode('rmousedown')
            if ev.type == pygame.MOUSEBUTTONUP:
                (xpos, ypos) = ev.pos
                if ev.button == 1:
                    self.last_lmouseup = self.grid_display.coords_from_mousepos(
                        xpos=xpos,
                        ypos=ypos)
                    return solent_keycode('lmouseup')
                if ev.button == 3:
                    self.last_rmouseup = self.grid_display.coords_from_mousepos(
                        xpos=xpos,
                        ypos=ypos)
                    return solent_keycode('rmouseup')
            if not ev.type == pygame.KEYDOWN:
                continue
            #
            c = _sanitise_input(
                u=ev.unicode)
            return c
    def block_get_keycode(self):
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
                return solent_keycode('mousedown')
            if ev.type == pygame.MOUSEBUTTONUP:
                (xpos, ypos) = ev.pos
                self.last_mouseup = self.grid_display.coords_from_mousepos(
                    xpos=xpos,
                    ypos=ypos)
                return solent_keycode('mouseup')
            if not ev.type == pygame.KEYDOWN:
                continue
            #
            c = _sanitise_input(
                u=ev.unicode)
            return c

DIR_STATIC = dget_static()
DIR_FONTS = os.sep.join( [DIR_STATIC, 'solent_console_pygame_fonts'] )
PATH_TTF_FONT = os.sep.join( [DIR_FONTS, 'kongtext', 'kongtext.ttf'] )
PYGAME_FONT_SIZE = 16

def pygame_console_new(width, height):
    pygame.font.init()
    font = pygame.font.Font(PATH_TTF_FONT, PYGAME_FONT_SIZE)
    window_console = PygameConsole(
        width=width,
        height=height,
        font=font)
    pygame.key.set_repeat(
        KEY_REPEAT_DELAY,
        KEY_REPEAT_INTERVAL)
    #
    ob = iconsole_new(
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

