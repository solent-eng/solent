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

from solent import e_cpair
from solent import e_keycode
from solent import key
from solent.console import cgrid_new
from solent.eng import engine_new
from solent.eng import nearcast_schema_new
from solent.exceptions import SolentQuitException
from solent.log import init_logging
from solent.log import log
from solent.menu import spin_menu_new
from solent.rogue import spin_message_feed_new
from solent.rogue.simple import spin_simple_new
from solent.term import spin_term_new
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

    message directive
        field directive_h
        field description
    message keycode_to_directive
        field control_scheme_h
        field keycode
        field directive_h

    message o_game_new
    message x_game_ready
    message x_game_grid
    message x_game_mail
    message x_game_over
    message o_game_focus
    message o_game_keycode
        field keycode
'''

CONTROL_SCHEME_H_GOLLOP = 'gollop'
CONTROL_SCHEME_H_KEYPAD = 'keypad'
CONTROL_SCHEME_H_VI = 'vi'

CONSOLE_HEIGHT = 24
CONSOLE_WIDTH = 80

MENU_KEYCODE_NEW_GAME = key('n')
MENU_KEYCODE_CONTINUE = key('c')
MENU_KEYCODE_QUIT = key('q')

ROGUEBOX_ORIGIN_DROP = 0
ROGUEBOX_ORIGIN_REST = 0

ROGUEBOX_GAMEBOX_HEIGHT = 23
ROGUEBOX_GAMEBOX_WIDTH = 23
ROGUEBOX_GAMEBOX_NAIL = (0, 0)
ROGUEBOX_GAMEBOX_PERI = (23, 23)

ROGUEBOX_MFEED_HEIGHT = CONSOLE_HEIGHT
ROGUEBOX_MFEED_WIDTH = 57
ROGUEBOX_MFEED_NAIL = (0, 23)
ROGUEBOX_MFEED_PERI = (24, 80)

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
    def on_o_game_focus(self):
        self.b_in_menu = False
    #
    def is_focus_on_menu(self):
        return self.b_in_menu
    def is_focus_on_game(self):
        return not self.b_in_menu

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
        self.d_directive = {}
    def on_quit(self):
        raise SolentQuitException('Quit message on stream')
    def on_directive(self, directive_h, description):
        self.d_directive[directive_h] = description
        #
        if directive_h == 'nw':
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_GOLLOP,
                keycode=e_keycode.q.value,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_KEYPAD,
                keycode=e_keycode.n7.value,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_VI,
                keycode=e_keycode.y.value,
                directive_h=directive_h)
        elif directive_h == 'nn':
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_GOLLOP,
                keycode=e_keycode.w.value,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_KEYPAD,
                keycode=e_keycode.n8.value,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_VI,
                keycode=e_keycode.k.value,
                directive_h=directive_h)
        elif directive_h == 'ne':
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_GOLLOP,
                keycode=e_keycode.e.value,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_KEYPAD,
                keycode=e_keycode.n9.value,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_VI,
                keycode=e_keycode.u.value,
                directive_h=directive_h)
        elif directive_h == 'sw':
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_GOLLOP,
                keycode=e_keycode.z.value,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_KEYPAD,
                keycode=e_keycode.n1.value,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_VI,
                keycode=e_keycode.b.value,
                directive_h=directive_h)
        elif directive_h == 'ss':
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_GOLLOP,
                keycode=e_keycode.x.value,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_KEYPAD,
                keycode=e_keycode.n2.value,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_VI,
                keycode=e_keycode.j.value,
                directive_h=directive_h)
        elif directive_h == 'se':
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_GOLLOP,
                keycode=e_keycode.c.value,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_KEYPAD,
                keycode=e_keycode.n3.value,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_VI,
                keycode=e_keycode.n.value,
                directive_h=directive_h)
        elif directive_h == 'ww':
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_GOLLOP,
                keycode=e_keycode.a.value,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_KEYPAD,
                keycode=e_keycode.n4.value,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_VI,
                keycode=e_keycode.h.value,
                directive_h=directive_h)
        elif directive_h == 'ee':
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_GOLLOP,
                keycode=e_keycode.d.value,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_KEYPAD,
                keycode=e_keycode.n6.value,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_VI,
                keycode=e_keycode.l.value,
                directive_h=directive_h)
        elif directive_h == 'bump':
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_GOLLOP,
                keycode=e_keycode.s.value,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_KEYPAD,
                keycode=e_keycode.n5.value,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_VI,
                keycode=e_keycode.space.value,
                directive_h=directive_h)
        elif directive_h == 'help':
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_VI,
                keycode=key('qmark'),
                directive_h=directive_h)
        else:
            raise Exception('Unhandled directive %s'%(directive.h))
    def on_keystroke(self, keycode):
        if self.pin_containment_mode.is_focus_on_menu():
            if keycode == key('tab'):
                self.b_in_menu = False
                self.nearcast.o_game_focus()
            else:
                self.nearcast.menu_select(
                    menu_keycode=keycode)
        else:
            if keycode == key('tab'):
                self.b_in_menu = True
                self.nearcast.menu_focus()
            else:
                self.nearcast.o_game_keycode(
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
        pass

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
    def on_o_game_new(self):
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
            cpair=e_cpair.blue_t)
    #
    def _mi_new_game(self):
        self.nearcast.o_game_new()
        self.nearcast.o_game_focus()
    def _mi_continue(self):
        self.nearcast.o_game_focus()
    def _mi_quit(self):
        raise SolentQuitException()

class CogRoguebox:
    '''
    Contains a roguelike game, and offers controls. The roguelike itself
    is contained to a 23x23 box in the top-left sector.
    Logging is offered in a box next to that.
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
        self.spin_message_feed = None
        self.cgrid_last = None
        self.cgrid_next = None
        self.d_keycode_to_directive = {}
        self.d_control_scheme = {} # (control_scheme_h, directive_h) = keycode
        #
        self.b_mail_waiting = False
        self.b_refresh_needed = False
    def close(self):
        pass
    def at_turn(self, activity):
        if self.spin_roguelike == None:
            return
        if not self.pin_containment_mode.is_focus_on_game():
            return
        if self.b_mail_waiting:
            activity.mark(
                l=self,
                s='mail processing')
            for message in self.spin_roguelike.retrieve_mail():
                self.spin_message_feed.accept(
                    message=message,
                    turn=self.spin_roguelike.get_turn())
            self.b_mail_waiting = False
            self.b_refresh_needed = True
        #
        if self.b_refresh_needed:
            self._diff_display_refresh()
            self.b_refresh_needed = False
    #
    def on_init(self, console_type, height, width):
        self.height = height
        self.width = width
        #
        if self.height < ROGUEBOX_GAMEBOX_HEIGHT:
            raise Exception("console height too small.")
        if self.width < ROGUEBOX_GAMEBOX_WIDTH:
            raise Exception("console width too small.")
        self.spin_roguelike = spin_simple_new(
            engine=self.engine,
            height=ROGUEBOX_GAMEBOX_HEIGHT,
            width=ROGUEBOX_GAMEBOX_WIDTH,
            cb_ready_alert=self._rl_ready_alert,
            cb_grid_alert=self._rl_grid_alert,
            cb_mail_alert=self._rl_mail_alert,
            cb_over_alert=self._rl_over_alert)
        self.spin_message_feed = spin_message_feed_new(
            height=ROGUEBOX_MFEED_HEIGHT,
            width=ROGUEBOX_MFEED_WIDTH,
            cpair_new=e_cpair.cyan_t,
            cpair_old=e_cpair.blue_t)
        self.cgrid_last = cgrid_new(
            width=width,
            height=height)
        self.cgrid_next = cgrid_new(
            width=width,
            height=height)
        #
        # sequence the possible directives in the game to the core. this will
        # give this outer core the opportunity to match directives it
        # recognises to keycodes. in the future, you could imagine being able
        # to configure user keystrokes using this data.
        for directive in self.spin_roguelike.get_supported_directives():
            self.nearcast.directive(
                directive_h=directive.h,
                description=directive.description)
    def on_keycode_to_directive(self, control_scheme_h, keycode, directive_h):
        self.d_keycode_to_directive[keycode] = directive_h
        self.d_control_scheme[ (control_scheme_h, directive_h) ] = keycode
    def on_x_game_ready(self):
        pass
    def on_o_game_new(self):
        self.spin_roguelike.new_game()
    def on_x_game_mail(self):
        self.b_mail_waiting = True
    def on_x_game_grid(self):
        self.b_refresh_needed = True
    def on_o_game_keycode(self, keycode):
        if keycode not in self.d_keycode_to_directive:
            return
        directive_h = self.d_keycode_to_directive[keycode]
        self.spin_roguelike.directive(
            directive_h=directive_h)
        self.spin_message_feed.scroll_past(
            turn=self.spin_roguelike.get_turn()-5)
        self.b_refresh_needed = True
    def on_o_game_focus(self):
        if None == self.spin_roguelike:
            self.nearcast.menu_focus()
            return
        self._full_display_refresh()
    #
    def _rl_ready_alert(self):
        self.nearcast.x_game_ready()
    def _rl_grid_alert(self):
        self.nearcast.x_game_grid()
    def _rl_mail_alert(self):
        self.nearcast.x_game_mail()
    def _rl_over_alert(self):
        self.nearcast.x_game_over()
    #
    def _full_display_refresh(self):
        self.nearcast.term_clear()
        self.cgrid_last.clear()
        self._diff_display_refresh()
    def _diff_display_refresh(self):
        self.spin_roguelike.get_cgrid(
            cgrid=self.cgrid_next,
            nail=ROGUEBOX_GAMEBOX_NAIL,
            peri=ROGUEBOX_GAMEBOX_PERI)
        self.spin_message_feed.get_cgrid(
            cgrid=self.cgrid_next,
            nail=ROGUEBOX_MFEED_NAIL,
            peri=ROGUEBOX_MFEED_PERI,
            turn=self.spin_roguelike.get_turn())
        #
        for drop in range(self.height):
            for rest in range(self.width):
                (old_c, old_cpair) = self.cgrid_last.get(
                    drop=drop,
                    rest=rest)
                (c, cpair) = self.cgrid_next.get(
                    drop=drop,
                    rest=rest)
                if c == old_c and cpair == old_cpair:
                    continue
                self.nearcast.term_write(
                    drop=drop,
                    rest=rest,
                    s=c,
                    cpair=cpair)
        #
        self.cgrid_last.blit(
            src_cgrid=self.cgrid_next)

def game(console_type):
    init_logging()
    #
    engine = None
    try:
        engine = engine_new(
            mtu=MTU)
        engine.set_default_timeout(0.04)
        #engine.debug_eloop_on()
        #
        nearcast_schema = nearcast_schema_new(
            i_nearcast=I_CONTAINMENT_NEARCAST_SCHEMA)
        orb = engine.init_orb(
            orb_h=__name__,
            nearcast_schema=nearcast_schema)
        #orb.add_log_snoop()
        orb.init_cog(CogInterpreter)
        orb.init_cog(CogTerm)
        orb.init_cog(CogMenu)
        orb.init_cog(CogRoguebox)
        #
        bridge = orb.init_cog(CogBridge)
        bridge.nc_init(
            console_type=console_type,
            height=CONSOLE_HEIGHT,
            width=CONSOLE_WIDTH)
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

