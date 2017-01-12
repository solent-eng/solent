#!/usr/bin/env python3
#
# roguebox
#
# // overview
# Nearcast that is designed to contain a roguelike game.
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

from solent import e_colpair
from solent import key
from solent.rogue.swamp_monster import spin_swamp_monster_new
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

# Containment consists of a menu system, a terminal, and cogs that
# encapsulate games.
I_CONTAINMENT_NEARCAST_SCHEMA = '''
    i message h
        i field h

    message init
        field console_type
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

class PinContainmentMode:
    '''
    Tracks whether we are in the menu or not.
    '''
    def __init__(self, orb):
        self.orb = orb
        #
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

class CogTerm:
    def __init__(self, cog_h, engine, orb):
        self.cog_h = cog_h
        self.engine = engine
        self.orb = orb
        #
        self.spin_term = None
    def close(self):
        if None != self.spin_term:
            self.spin_term.close()
    def at_turn(self, activity):
        self.spin_term.at_turn(
            activity=activity)
    #
    def on_init(self, console_type, height, width):
        self.spin_term = spin_term_new(
            console_type=console_type,
            cb_keycode=self.term_on_keycode,
            cb_select=self.term_on_select)
        self.spin_term.open_console(
            width=width,
            height=height)
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

class CogMenu:
    def __init__(self, cog_h, engine, orb):
        self.cog_h = cog_h
        self.engine = engine
        self.orb = orb
        #
        self.spin_menu = None
    def close(self):
        pass
    def on_init(self, console_type, height, width):
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

ROGUEBOX_GAME_HEIGHT = 23
ROGUEBOX_GAME_WIDTH = 23

class CogRoguebox:
    '''
    Contains a roguelike game, and offers controls. The roguelike itself
    is contained to a 23x23 box in the top-left sector.
    '''
    def __init__(self, cog_h, engine, orb):
        self.cog_h = cog_h
        self.engine = engine
        self.orb = orb
        #
        self.pin_containment_mode = orb.init_pin(PinContainmentMode)
        self.height = None
        self.width = None
        self.spin_roguelike = None
    def close(self):
        pass
    def at_turn(self, activity):
        if self.spin_roguelike == None:
            return
        if not self.pin_containment_mode.is_focus_on_game():
            return
    #
    def on_init(self, console_type, height, width):
        self.height = height
        self.width = width
    def on_game_new(self):
        self.spin_roguelike = spin_swamp_monster_new(
            engine=self.engine,
            height=ROGUEBOX_GAME_HEIGHT,
            width=ROGUEBOX_GAME_WIDTH,
            cb_cls=self.rl_cls,
            cb_put=self.rl_put,
            cb_box=self.rl_box)
    def on_game_input(self, keycode):
        if keycode in (key('q'), key('y'), key('n7')):
            self.spin_roguelike.input_nw()
        elif keycode in (key('w'), key('k'), key('n8')):
            self.spin_roguelike.input_nn()
        elif keycode in (key('e'), key('u'), key('n9')):
            self.spin_roguelike.input_ne()
        elif keycode in (key('z'), key('b'), key('n1')):
            self.spin_roguelike.input_sw()
        elif keycode in (key('x'), key('j'), key('n2')):
            self.spin_roguelike.input_ss()
        elif keycode in (key('c'), key('n'), key('n3')):
            self.spin_roguelike.input_se()
        elif keycode in (key('a'), key('h'), key('n4')):
            self.spin_roguelike.input_ww()
        elif keycode in (key('d'), key('l'), key('n6')):
            self.spin_roguelike.input_ee()
        elif keycode in (key('s'), key('newline'), key('space'), key('n5')):
            self.spin_roguelike.input_bump()
    def on_game_focus(self):
        if self.spin_roguelike == None:
            self.nearcast.menu_focus()
            return
        self.spin_roguelike.full_refresh()
    #
    def rl_cls(self):
        self.nearcast.term_clear()
    def rl_put(self, drop, rest, s, cpair):
        self.nearcast.term_write(
            drop=drop,
            rest=rest,
            s=s,
            cpair=cpair)
    def rl_box(self, message):
        self.nearcast.term_clear()
        lines = message.split('\n')
        #
        height = len(lines)
        width = max([len(l) for l in lines])
        drop_offset = int( (self.height - height) / 2 )
        rest_offset = int( (self.width - width) / 2 )
        #
        for idx, line in enumerate(lines):
            self.nearcast.term_write(
                drop=drop_offset+idx,
                rest=rest_offset,
                s=line,
                cpair=e_colpair.white_t)

class CogBridge:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
    def nc_init(self, console_type, height, width):
        self.nearcast.init(
            console_type=console_type,
            height=height,
            width=width)

def game(console_type):
    init_logging()
    #
    engine = None
    try:
        engine = engine_new(
            mtu=MTU)
        engine.set_default_timeout(0.04)
        engine.debug_eloop_on() # xxx
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
        orb.init_cog(CogRoguebox)
        #
        bridge = orb.init_cog(CogBridge)
        bridge.nc_init(
            console_type=console_type,
            height=24,
            width=80)
        #
        engine.event_loop()
    except SolentQuitException:
        pass
    except:
        traceback.print_exc()
    finally:
        if engine != None:
            engine.close()

def main():
    #
    if '--curses' in sys.argv:
        console_type = 'curses'
    elif '--pygame' in sys.argv:
        console_type = 'pygame'
    else:
        print('ERROR: specify a terminal type! (curses, pygame)')
        sys.exit(1)
    #
    game(console_type)

if __name__ == '__main__':
    main()

