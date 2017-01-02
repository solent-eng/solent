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

from solent.console import e_colpair
from solent.console import key
from solent.eng import engine_new
from solent.eng import nearcast_schema_new
from solent.exceptions import SolentQuitException
from solent.log import init_logging
from solent.log import log
from solent.term import spin_term_new
from solent.menu import spin_menu_new
from solent.util import uniq

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
    def __init__(self, height, width, cb_display_clear, cb_display_write):
        self.height = height
        self.width = width
        self.cb_display_clear = cb_display_clear
        self.cb_display_write = cb_display_write
    def render_game(self):
        self.cb_display_clear()
        self.cb_display_write(
            drop=0,
            rest=0,
            s='[game]',
            cpair=e_colpair.green_t)

def spin_snake_game_new(height, width, cb_display_clear, cb_display_write):
    '''
    cb_display_clear()
    cb_display_write(drop, rest, s, cpair)
    '''
    ob = SpinSnakeGame(
        height=height,
        width=width,
        cb_display_clear=cb_display_clear,
        cb_display_write=cb_display_write)
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

    message quit

    message keystroke
        field keycode

    message game_focus
    message game_new
    message game_input
        field keycode

    message term_clear
    message term_write
        field drop
        field rest
        field s
        field cpair

    message menu_focus
    message menu_title
        field text
    message menu_item
        field menu_keycode
        field text
    message menu_select
        field menu_keycode
'''

MENU_KEYCODE_NEW_GAME = key('n')
MENU_KEYCODE_CONTINUE = key('c')
MENU_KEYCODE_QUIT = key('q')

def t100():
    return time.time() * 100

class CogInterpreter(object):
    '''
    Coordinates high-level concepts such as whether we are in a menu or in the
    game.
    '''
    def __init__(self, cog_h, engine, orb):
        self.cog_h = cog_h
        self.engine = engine
        self.orb = orb
        #
        self.b_in_menu = False
    def on_init(self, height, width):
        self.b_in_menu = True
    def on_quit(self):
        raise SolentQuitException('Quit message on stream')
    def on_menu_focus(self):
        self.b_in_menu = True
    def on_game_focus(self):
        self.b_in_menu = False
    def on_keystroke(self, keycode):
        # xxx
        if keycode == ord('Q'):
            self.nearcast.quit()
        #
        if self.b_in_menu:
            if keycode == key('tab'):
                self.b_in_menu = False
                self.nearcast.game_focus()
            else:
                self.nearcast.menu_select(
                    menu_keycode=keycode)
        else:
            if keycode == key('tab'):
                self.b_in_menu = True
                self.nearcast.menu_focus()
            else:
                self.nearcast.game_input(
                    keycode=keycode)

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
    def on_term_clear(self):
        self.spin_term.clear()
    def on_term_write(self, drop, rest, s, cpair):
        self.spin_term.write(
            drop=drop,
            rest=rest,
            s=s,
            cpair=cpair)
    #
    def term_on_keycode(self, keycode):
        self.nearcast.keystroke(
            keycode=keycode)
    def term_on_select(self, drop, rest):
        # user makes a selection
        log('xxx term_on_select drop %s rest %s'%(drop, rest))
    #
    def on_init(self, height, width):
        self.spin_term.open_console(
            width=width,
            height=height)

class CogMenu(object):
    def __init__(self, cog_h, engine, orb):
        self.cog_h = cog_h
        self.engine = engine
        self.orb = orb
        #
        self.spin_menu = None
    def close(self):
        pass
    def on_init(self, height, width):
        self.spin_menu = spin_menu_new(
            height=height,
            width=width,
            cb_display_clear=self.menu_display_clear,
            cb_display_write=self.menu_display_write)
        self.nearcast.menu_title(
            text=__name__)
        self.nearcast.menu_item(
            menu_keycode=MENU_KEYCODE_NEW_GAME,
            text='new game')
        self.nearcast.menu_item(
            menu_keycode=MENU_KEYCODE_CONTINUE,
            text='continue')
        self.nearcast.menu_item(
            menu_keycode=MENU_KEYCODE_QUIT,
            text='quit')
        self.nearcast.menu_focus()
    def on_menu_title(self, text):
        self.spin_menu.set_title(
            text=text)
    def on_menu_item(self, menu_keycode, text):
        self.spin_menu.add_menu_item(
            menu_keycode=menu_keycode,
            text=text,
            cb_select=lambda: self.menu_select(
                menu_keycode=keycode))
    def on_menu_focus(self):
        self.spin_menu.render_menu()
    def on_menu_select(self, menu_keycode):
        d = { MENU_KEYCODE_NEW_GAME: self._mi_new_game
            , MENU_KEYCODE_CONTINUE: self._mi_continue
            , MENU_KEYCODE_QUIT: self._mi_quit
            }
        if menu_keycode not in d:
            return
        fn = d[menu_keycode]
        fn()
    #
    def menu_select(self, menu_keycode):
        self.nearcast.menu_select(
            menu_keycode=menu_keycode)
    def menu_display_clear(self):
        self.nearcast.term_clear()
    def menu_display_write(self, drop, rest, s):
        self.nearcast.term_write(
            drop=drop,
            rest=rest,
            s=s,
            cpair=e_colpair.blue_t)
    #
    def _mi_new_game(self):
        self.nearcast.game_new()
        self.nearcast.game_focus()
    def _mi_continue(self):
        raise Exception('xxx continue game')
    def _mi_quit(self):
        raise SolentQuitException()

class CogSnakeGame:
    def __init__(self, cog_h, engine, orb):
        self.cog_h = cog_h
        self.engine = engine
        self.orb = orb
        #
        self.height = None
        self.width = None
        self.spin_snake_game = None
    def on_init(self, height, width):
        self.height = height
        self.width = width
    def on_game_new(self):
        self.spin_snake_game = spin_snake_game_new(
            height=self.height,
            width=self.width,
            cb_display_clear=self.game_display_clear,
            cb_display_write=self.game_display_write)
    def on_game_input(self, keycode):
        raise Exception('xxx')
    def on_game_focus(self):
        if None == self.spin_snake_game:
            self.nearcast.menu_focus()
            return
        self.spin_snake_game.render_game()
    #
    def game_display_clear(self):
        self.nearcast.term_clear()
    def game_display_write(self, drop, rest, s, cpair):
        self.nearcast.term_write(
            drop=drop,
            rest=rest,
            s=s,
            cpair=cpair)

class CogPrimer:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
    def nc_init(self, height, width):
        self.nearcast.init(
            height=height,
            width=width)

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
        orb.add_log_snoop()
        orb.init_cog(CogInterpreter)
        orb.init_cog(CogTerm)
        orb.init_cog(CogMenu)
        orb.init_cog(CogSnakeGame)
        #
        primer = orb.init_cog(CogPrimer)
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

