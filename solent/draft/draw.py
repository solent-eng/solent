#!/usr/bin/env python3
#
# draw
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
import random
import sys
import time
import traceback

MTU = 1500


# --------------------------------------------------------
#   :game
# --------------------------------------------------------
def create_spot(drop, rest):
    return (drop, rest)

class SpinDrawGame:
    def __init__(self, height, width, cb_display_clear, cb_display_write):
        self.height = height
        self.width = width
        self.cb_display_clear = cb_display_clear
        self.cb_display_write = cb_display_write
        #
        self.spots = []
    def tick(self):
        pass
    def render(self):
        self.cb_display_clear()
        for spot in self.spots:
            (drop, rest) = spot
            self.cb_display_write(
                drop=drop,
                rest=rest,
                s='@',
                cpair=e_colpair.yellow_t)
    def flip(self, drop, rest):
        spot = create_spot(drop, rest)
        if spot in self.spots:
            self.spots.remove(spot)
        else:
            self.spots.append(spot)

def spin_draw_game_new(height, width, cb_display_clear, cb_display_write):
    '''
    cb_display_clear()
    cb_display_write(drop, rest, s, cpair)
    '''
    ob = SpinDrawGame(
        height=height,
        width=width,
        cb_display_clear=cb_display_clear,
        cb_display_write=cb_display_write)
    return ob


# --------------------------------------------------------
#   :containment
# --------------------------------------------------------
#
# Containment consists of a menu system, a terminal, and a cog that
# encapsulates the game.
#
I_CONTAINMENT_NEARCAST_SCHEMA = '''
    i message h
        i field h

    message init
        field height
        field width

    message quit

    message keystroke
        field keycode
    message tselect
        # mouse or gollop selection from the term
        field drop
        field rest

    message game_focus
    message game_new
    message game_input
        field keycode
    message game_plot
        field drop
        field rest

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

class PinContainmentMode:
    '''
    Tracks whether we are in the menu or not.
    '''
    def __init__(self):
        self.b_in_menu = True
    #
    def on_menu_focus(self):
        self.b_in_menu = True
    def on_game_focus(self):
        self.b_in_menu = False
    #
    def is_focus_on_menu(self):
        return self.b_in_menu
    def is_focus_on_game(self):
        return not self.b_in_menu

class CogInterpreter:
    '''
    Coordinates high-level concepts such as whether we are in a menu or in the
    game.
    '''
    def __init__(self, cog_h, engine, orb):
        self.cog_h = cog_h
        self.engine = engine
        self.orb = orb
        #
        self.pin_containment_mode = orb.init_pin(PinContainmentMode)
    def on_quit(self):
        raise SolentQuitException('Quit message on stream')
    def on_keystroke(self, keycode):
        if self.pin_containment_mode.is_focus_on_menu():
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
    def on_tselect(self, drop, rest):
        if self.pin_containment_mode.is_focus_on_game():
            self.nearcast.game_plot(
                drop=drop,
                rest=rest)

class CogTerm:
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
        self.nearcast.tselect(
            drop=drop,
            rest=rest)
    #
    def on_init(self, height, width):
        self.spin_term.open_console(
            width=width,
            height=height)

class CogMenu:
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
    def on_game_new(self):
        if not self.spin_menu.has_menu_keycode(MENU_KEYCODE_CONTINUE):
            self.nearcast.menu_item(
                menu_keycode=MENU_KEYCODE_CONTINUE,
                text='continue')
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
        self.nearcast.game_focus()
    def _mi_quit(self):
        raise SolentQuitException()

class CogDrawGame:
    def __init__(self, cog_h, engine, orb):
        self.cog_h = cog_h
        self.engine = engine
        self.orb = orb
        #
        self.pin_containment_mode = orb.init_pin(PinContainmentMode)
        self.height = None
        self.width = None
        self.spin_draw_game = None
        self.tick_t100 = None
    def close(self):
        pass
    def at_turn(self, activity):
        if self.spin_draw_game == None:
            return
    #
    def on_init(self, height, width):
        self.height = height
        self.width = width
    def on_game_new(self):
        self.spin_draw_game = spin_draw_game_new(
            height=self.height,
            width=self.width,
            cb_display_clear=self.game_display_clear,
            cb_display_write=self.game_display_write)
    def on_game_input(self, keycode):
        log('xxx game input %s'%keycode)
    def on_game_focus(self):
        self.spin_draw_game.render()
    def on_game_plot(self, drop, rest):
        self.spin_draw_game.flip(
            drop=drop,
            rest=rest)
        self.spin_draw_game.render()
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
        engine.default_timeout = 0.05
        #
        nearcast_schema = nearcast_schema_new(
            i_nearcast=I_CONTAINMENT_NEARCAST_SCHEMA)
        orb = engine.init_orb(
            orb_h=__name__,
            nearcast_schema=nearcast_schema)
        orb.add_log_snoop()
        orb.init_cog(CogInterpreter)
        orb.init_cog(CogTerm)
        orb.init_cog(CogMenu)
        orb.init_cog(CogDrawGame)
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

