#!/usr/bin/env python3
#
# menu box
#
# // overview
# Sandbox used for developing spin_menu.
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

I_NEARCAST_SCHEMA = '''
    i message h
        i field h

    message init
        field console_type
        field height
        field width

    # tell the menu to display
    message menu_display

    # title to put above the menu
    message menu_title
        field text

    # define a menu item
    message menu_item
        field menu_keycode
        field text

    # select an item from the menu
    message menu_select
        field menu_keycode

    message keystroke
        field keycode

    # tell the game to display (after a mode change)
    message game_display

    # send input towards the game
    message game_input
        field keycode

    # tell the terminal to clear
    message term_clear

    # tell the terminal to write
    message term_write
        field drop
        field rest
        field s
'''

MENU_KEYCODE_NEW_GAME = solent_keycode('n')
MENU_KEYCODE_CONTINUE = solent_keycode('c')
MENU_KEYCODE_QUIT = solent_keycode('q')

class CogInterpreter(object):
    '''
    Keeps track of whether we are in menu or not, and directs keystrokes as
    appropriate.
    '''
    def __init__(self, cog_h, engine, orb):
        self.cog_h = cog_h
        self.engine = engine
        self.orb = orb
        #
        self.is_in_menu = False
    def on_init(self, console_type, height, width):
        self.is_in_menu = True
    def on_keystroke(self, keycode):
        log('key received %s'%(hex(keycode)))
        if keycode == solent_keycode('Q'):
            raise SolentQuitException()
        if self.is_in_menu:
            if keycode == solent_keycode('tab'):
                self.is_in_menu = False
            self.nearcast.menu_select(
                menu_keycode=keycode)
        else:
            self.nearcast.game_input(
                keycode=keycode)

class CogTerm(object):
    def __init__(self, cog_h, engine, orb):
        self.cog_h = cog_h
        self.engine = engine
        self.orb = orb
        #
        self.spin_term = None
    def close(self):
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
            height=height,
            width=width)
    def on_term_clear(self):
        self.spin_term.clear()
    def on_term_write(self, drop, rest, s):
        self.spin_term.write(
            drop=drop,
            rest=rest,
            s=s,
            cpair=solent_cpair('white'))
    #
    def term_on_keycode(self, keycode):
        self.nearcast.keystroke(
            keycode=keycode)
    def term_on_select(self, drop, rest):
        # user makes a selection
        log('xxx term_on_select drop %s rest %s'%(drop, rest))

class CogMenu(object):
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
            menu_keycode=MENU_KEYCODE_CONTINUE,
            text='continue')
        self.nearcast.menu_item(
            menu_keycode=MENU_KEYCODE_QUIT,
            text='quit')
        self.nearcast.menu_display()
    def on_menu_title(self, text):
        self.spin_menu.set_title(
            text=text)
    def on_menu_item(self, menu_keycode, text):
        self.spin_menu.add_menu_item(
            menu_keycode=menu_keycode,
            text=text,
            cb_select=lambda: self.menu_select(
                menu_keycode=keycode))
    def on_menu_display(self):
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
            s=s)
    #
    def _mi_new_game(self):
        raise Exception('xxx new game')
    def _mi_continue(self):
        raise Exception('xxx continue game')
    def _mi_quit(self):
        raise SolentQuitException()

class CogBridge(object):
    def __init__(self, cog_h, engine, orb):
        self.cog_h = cog_h
        self.engine = engine
        self.orb = orb
    def nc_init(self, console_type, height, width):
        self.nearcast.init(
            console_type=console_type,
            height=height,
            width=width)
    def nc_menu_title(self, text):
        self.nearcast.menu_title(
            text=text)
    def nc_menu_item(self, menu_keycode, text):
        self.nearcast.menu_item(
            menu_keycode=menu_keycode,
            text=text)

HEIGHT = 25
WIDTH = 80

def main():
    if '--curses' in sys.argv:
        console_type = 'curses'
    elif '--pygame' in sys.argv:
        console_type = 'pygame'
    else:
        print('ERROR: specify either --curses or --pygame')
        sys.exit(1)
    #
    init_logging()
    #
    engine = None
    try:
        engine = engine_new(
            mtu=MTU)
        engine.default_timeout = 0.04
        #
        nearcast_schema = nearcast_schema_new(
            i_nearcast=I_NEARCAST_SCHEMA)
        orb = engine.init_orb(
            orb_h=__name__,
            nearcast_schema=nearcast_schema)
        orb.add_log_snoop()
        orb.init_cog(CogInterpreter)
        orb.init_cog(CogTerm)
        orb.init_cog(CogMenu)
        #
        bridge = orb.init_cog(CogBridge)
        bridge.nc_init(
            console_type=console_type,
            height=HEIGHT,
            width=WIDTH)
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

