#!/usr/bin/env python3
#
# snake
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

from solent.eng import engine_new
from solent.eng import nearcast_schema_new
from solent.exceptions import SolentQuitException
from solent.log import init_logging
from solent.log import log
from solent.term import spin_term_new
from solent.util import uniq
from solent.winconsole import window_console_new

from collections import deque
import os
import sys
import time
import traceback

MTU = 1500


# --------------------------------------------------------
#   :game
# --------------------------------------------------------
I_GAME_NEARCAST_SCHEMA = '''
    i message h
        i field h

    message game_start
    message game_pause

    message canvas_clear
    message canvas_create_snake
    message canvas_grow_snake

    message snake_up
    message snake_down
    message snake_left
    message snake_right

    message keystroke
        field keycode
'''

class SpinSnakeGame:
    def __init__(self):
        pass

def spin_snake_game_new():
    ob = SpinSnakeGame()
    return ob


# --------------------------------------------------------
#   :outer
# --------------------------------------------------------
I_OUTER_NEARCAST_SCHEMA = '''
    i message h
        i field h

    message init
        field height
        field width

    message show_game_menu
    message new_game
    message continue
    message quit

    message term_clear
    message term_plot
        field drop
        field rest
        field c

    message keystroke
        field keycode
'''

class MenuWaiter:
    '''
    Tracks whether we are in the menu or not.
    '''
    def __init__(self):
        self.in_menu = False
    def on_init(self, width, height):
        self.in_menu = True
    def 

def t100():
    return time.time() * 100

class CogPrimer:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
    def nc_show_menu(self):
        self.orb.nearcast(
            cog=self,
            message_h='show_menu')
    def nc_init(self, height, width):
        self.orb.nearcast(
            cog=self,
            message_h='init',
            height=height,
            width=width)

class CogTerm(object):
    def __init__(self, cog_h, engine, orb):
        self.cog_h = cog_h
        self.engine = engine
        self.orb = orb
        #
        self.spin_term = spin_term_new(
            cb_keycode=self.term_on_keycode,
            cb_select=self.term_on_select)
    def close(self):
        self.spin_term.close()
    def at_turn(self, activity):
        self.spin_term.at_turn(
            activity=activity)
    #
    def term_on_keycode(self, keycode):
        self.orb.nearcast(
            cog=self,
            message_h='keystroke',
            keycode=keycode)
    def term_on_select(self, drop, rest):
        # user makes a selection
        log('xxx term_on_select drop %s rest %s'%(drop, rest))
    #
    def on_init(self, height, width):
        self.spin_term.open_console(
            width=width,
            height=height)

class CogButler(object):
    '''
    Coordinates high-level concepts such as whether we are in a menu or in the
    game.
    '''
    def __init__(self, cog_h, engine, orb):
        self.cog_h = cog_h
        self.engine = engine
        self.orb = orb
        #
        self.menu_waiter = MenuWaiter()
    def on_init(self, width, height):
        self.menu_waiter.on_init(
            width=width,
            height=height)
        self.orb.nearcast(
            cog=self,
            message_h='show_game_menu')
    def on_show_game_menu(self):
        log('xxx!')
    def on_butler_show_menu(self):
        self.orb.nearcast(
            cog=self,
            message_h='canvas_clear')
    def on_quit(self):
        raise SolentQuitException('Quit message on stream')
    def on_keystroke(self, keycode):
        if keycode == ord('Q'):
            self.orb.nearcast(
                cog=self,
                message_h='quit')

class CogGame:
    def __init__(self, cog_h, engine, orb):
        self.cog_h = cog_h
        self.engine = engine
        self.orb = orb

def main():
    init_logging()
    #
    engine = None
    try:
        engine = engine_new(
            mtu=MTU)
        engine.default_timeout = 0.04
        #
        nearcast_schema = nearcast_schema_new(
            i_nearcast=I_OUTER_NEARCAST_SCHEMA)
        orb = engine.init_orb(
            orb_h=__name__,
            nearcast_schema=nearcast_schema)
        primer = orb.init_cog(CogPrimer)
        orb.init_cog(CogTerm)
        orb.init_cog(CogButler)
        orb.init_cog(CogGame)
        #
        primer.nc_init(
            height=24,
            width=78)
        #
        engine.event_loop()
    except SolentQuitException:
        pass
    except:
        traceback.print_exc()
    finally:
        if engine != None:
            engine.close()

if __name__ == '__main__':
    main()

