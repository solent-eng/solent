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
#
# // overview
# Nearcast that is contains a simple roguelike game.

from solent import Engine
from solent import e_keycode
from solent import init_network_logging
from solent import log
from solent import solent_cpair
from solent import solent_keycode
from solent import SolentQuitException
from solent import uniq
from solent.console import Cgrid
from solent.console import RailMenu
from solent.util import SpinSelectionUi

from collections import deque
import os
import platform
import random
import sys
import time
import traceback


# --------------------------------------------------------
#   utility rails
# --------------------------------------------------------
class RailMessageFeed:
    '''
    This accepts text messages, and then renders them to a cgrid. Imagine text
    as it is coming out of an old-fashioned printer, on a feed of paper.

    There are two general use-cases for retrieving data from this:
    * You can call list_messages, and get back a list of current messages
    * You can call get_cgrid, and it will populate your supplied grid
    '''

    def __init__(self):
        pass
    def zero(self, rail_h, height, width, cpair_new, cpair_old):
        self.rail_h = rail_h
        self.height = height
        self.width = width
        self.cpair_new = cpair_new
        self.cpair_old = cpair_old
        #
        self.cgrid = Cgrid(
            height=height,
            width=width)
        self.q_lines = deque()
    def clear(self):
        while self.q_lines:
            self.scroll()
    def accept(self, message, turn):
        nail = 0
        peri = nail+self.width
        while len(message) > peri:
            self._write(
                text=message[nail:peri],
                turn=turn)
            nail = peri
            peri = peri + self.width
        self._write(
            text=message[nail:peri],
            turn=turn)
    def scroll(self):
        self.q_lines.popleft()
    def scroll_past(self, turn):
        while self.q_lines:
            first_pair = self.q_lines[0]
            message_turn = first_pair[1]
            if message_turn <= turn:
                self.scroll()
            else:
                break
    def get_height(self):
        return len(self.q_lines)
    def list_messages(self):
        sb = []
        for (message, turn) in self.q_lines:
            sb.append(message)
        return sb
    def get_cgrid(self, cgrid, nail, peri, turn):
        self.cgrid.clear()
        for idx, (line, mturn) in enumerate(self.q_lines):
            if mturn == turn:
                cpair = self.cpair_new
            else:
                cpair = self.cpair_old
            self.cgrid.put(
                drop=idx,
                rest=0,
                s=line,
                cpair=cpair)
        cgrid.blit(
            self.cgrid,
            nail=nail,
            peri=peri)
    def _write(self, text, turn):
        self.q_lines.append( (text, turn) )
        while len(self.q_lines) > self.height:
            self.q_lines.popleft()


# --------------------------------------------------------
#   roguebox
# --------------------------------------------------------
#
# This section contains the logic of the game board.
#

class Directive:
    def __init__(self, h, description):
        self.h = h
        self.description = description

# We reflect against global to get these
DIRECTIVE_HELP = Directive('help', 'show help message')
DIRECTIVE_BX = Directive('a', 'button')
DIRECTIVE_BY = Directive('b', 'button')
DIRECTIVE_NW = Directive('nw', 'move/act in this direction')
DIRECTIVE_NN = Directive('nn', 'move/act in this direction')
DIRECTIVE_NE = Directive('ne', 'move/act in this direction')
DIRECTIVE_SW = Directive('sw', 'move/act in this direction')
DIRECTIVE_SS = Directive('ss', 'move/act in this direction')
DIRECTIVE_SE = Directive('se', 'move/act in this direction')
DIRECTIVE_WW = Directive('ww', 'move/act in this direction')
DIRECTIVE_EE = Directive('ee', 'move/act in this direction')

HELP = '''Hit things with your crowbar. Survive.

Movement:
 q w e      7 8 9       y k u
 a   d      4   6       h   l
 z x d      1 2 3       b j n

Buttons
a:  s          5           space
b:  r          plus        slash

(Tab returns to the main menu.)
'''

PAIR_WALL = ('.', solent_cpair('blue'))
PAIR_PLAYER = ('@', solent_cpair('green'))
PAIR_WEED = ('t', solent_cpair('red'))

class RailRoguebox:
    def __init__(self):
        pass
    def zero(self, rail_h, engine, grid_height, grid_width, cb_ready_alert, cb_grid_alert, cb_mail_alert, cb_over_alert):
        self.rail_h = rail_h
        self.engine = engine
        self.grid_height = grid_height
        self.grid_width = grid_width
        self.cb_grid_alert = cb_grid_alert
        self.cb_mail_alert = cb_mail_alert
        self.cb_ready_alert = cb_ready_alert
        self.cb_over_alert = cb_over_alert

        self.turn = 0
        self.b_game_alive = False

        #
        # coordinate pools
        self.cpool_spare = None
        self.cpool_wall = None
        self.cpool_player = None
        self.cpool_weed = None

        self.supported_directives = None
        self._init_supported_directives()

        self.cgrid = Cgrid(
            height=grid_height,
            width=grid_width)
        self.q_mail_messages = deque()

        self.orb = None
        self._init_orb()

        self.bridge = self.orb.init_autobridge()
        self.bridge.nc_init(
            grid_height=self.grid_height,
            grid_width=self.grid_width)

    def _init_supported_directives(self):
        self.supported_directives = [
            globals()[key] for key
            in globals().keys()
            if key.startswith('DIRECTIVE_')]

    def _init_orb(self):
        i_nearcast = '''
            i message h
                i field h

            message init
                field grid_height
                field grid_width
        '''
        self.orb = self.engine.init_orb(
            i_nearcast=i_nearcast)
        self.orb.set_spin_h('swamp_monster_orb')
        #self.orb.add_log_snoop()

    def get_supported_directives(self):
        '''
        Returns list of instances of solent.rogue.directive representing
        the directives that this instance cares about. The reason for this
        design is that it allows the container to handle input configuration.
        For example, if you want the number 7 to mean north-east, you will
        want to be able to configure that. And it would be a distraction from
        the game engine itself.
        '''
        return self.supported_directives[:]

    def new_game(self):
        self.turn = 0
        self.b_game_alive = True

        self._zero_coord_pools()
        self._create_board()

        self.cb_ready_alert()

        self._announce("You are in the garden. Eliminate those evil weeds!")
        self._announce("[Press ? for help]")

    def _zero_coord_pools(self):
        self.cpool_spare = []
        self.cpool_wall = []
        self.cpool_player = []
        self.cpool_weed = []

        room_width = 10
        room_height = 10
        nail_drop = int( (self.grid_height / 2) - (room_height / 2) )
        nail_rest = int( (self.grid_width / 2) - (room_width / 2) )
        peri_drop = nail_drop + room_width + 1
        peri_rest = nail_rest + room_height + 1
        for drop in range(nail_drop, peri_drop):
            for rest in range(nail_rest, peri_rest):
                self.cpool_spare.append( (drop, rest) )

    def get_turn(self):
        return self.turn

    def get_cgrid(self, cgrid, nail, peri):
        self._render_cgrid()
        cgrid.blit(
            src_cgrid=self.cgrid,
            nail=nail,
            peri=peri)

    def retrieve_mail(self):
        l = []
        while self.q_mail_messages:
            l.append(self.q_mail_messages.popleft())
        return l

    def directive(self, directive_h):
        if directive_h == 'help':
            for line in HELP.split('\n'):
                self._announce(line)
            return
        if False == self.b_game_alive:
            return
        else:
            self.turn += 1

            player_spot = self.cpool_player[0]
            target_spot = list(player_spot)
            if directive_h in 'nw|ww|sw'.split('|'):
                target_spot[1] -= 1
            if directive_h in 'ne|ee|se'.split('|'):
                target_spot[1] += 1
            if directive_h in 'nw|nn|ne'.split('|'):
                target_spot[0] -= 1
            if directive_h in 'sw|ss|se'.split('|'):
                target_spot[0] += 1
            self._player_move(
                player_spot=player_spot,
                target_spot=tuple(target_spot))
            if 0 == len(self.cpool_weed):
                self._announce('You win!')
                self._game_over()

    def _player_move(self, player_spot, target_spot):
        if target_spot in self.cpool_spare:
            self.cpool_player.remove(player_spot)
            self.cpool_spare.append(player_spot)
            self.cpool_spare.remove(target_spot)
            self.cpool_player.append(target_spot)
            self.cb_grid_alert()
            return
        elif target_spot in self.cpool_weed:
            self._announce(
                message='You slash angrily at the weed!')
            self.cpool_player.remove(player_spot)
            self.cpool_spare.append(player_spot)
            self.cpool_weed.remove(target_spot)
            self.cpool_player.append(target_spot)
            self.cb_grid_alert()

    def _announce(self, message):
        self.q_mail_messages.append(message)
        self.cb_mail_alert()

    def _game_over(self):
        self.b_game_alive = False
        self.cb_over_alert()

    def _create_board(self):
        coord = ( int(self.grid_height/2), int(self.grid_width/2) )
        self.cpool_spare.remove(coord)
        self.cpool_player.append(coord)
        #
        # create the walls
        room_width = 10
        room_height = 10
        nail_drop = int( (self.grid_height / 2) - (room_height / 2) )
        nail_rest = int( (self.grid_width / 2) - (room_width / 2) )
        peri_drop = nail_drop + room_width + 1
        peri_rest = nail_rest + room_height + 1
        # horizontal walls, including corners
        for rest in range(nail_rest, peri_rest):
            coord = (nail_drop, rest)
            self.cpool_spare.remove(coord)
            self.cpool_wall.append(coord)
            coord = (nail_drop+room_height, rest)
            self.cpool_spare.remove(coord)
            self.cpool_wall.append(coord)
        # vertical walls, except corners
        for drop in range(nail_drop+1, peri_drop-1):
            coord = (drop, nail_rest)
            self.cpool_spare.remove(coord)
            self.cpool_wall.append(coord)
            coord = (drop, nail_rest+room_width)
            self.cpool_spare.remove(coord)
            self.cpool_wall.append(coord)
        #
        # place weeds
        # (we need at least one.)
        while not self.cpool_weed:
            for coord in self.cpool_spare:
                (drop, rest) = coord
                if drop < 8 or drop > 16:
                    continue
                if rest < 34 or rest > 46:
                    continue
                if random.random() > 0.98:
                    self.cpool_spare.remove(coord)
                    self.cpool_weed.append(coord)

    def _render_cgrid(self):
        self.cgrid.clear()
        for coord in self.cpool_spare:
            (drop, rest) = coord
            (c, cpair) = (' ', solent_cpair('teal'))
            self.cgrid.put(
                drop=drop,
                rest=rest,
                s=c,
                cpair=cpair)
        for coord in self.cpool_wall:
            (drop, rest) = coord
            (c, cpair) = PAIR_WALL
            self.cgrid.put(
                drop=drop,
                rest=rest,
                s=c,
                cpair=cpair)
        for coord in self.cpool_player:
            (drop, rest) = coord
            (c, cpair) = PAIR_PLAYER
            if not self.b_game_alive:
                cpair = solent_cpair('blue')
            self.cgrid.put(
                drop=drop,
                rest=rest,
                s=c,
                cpair=cpair)
        for coord in self.cpool_weed:
            (drop, rest) = coord
            (c, cpair) = PAIR_WEED
            self.cgrid.put(
                drop=drop,
                rest=rest,
                s=c,
                cpair=cpair)


# --------------------------------------------------------
#   main nearcast
# --------------------------------------------------------
# Containment consists of a menu system, a terminal, and cogs that
# encapsulate games.
I_CONTAINMENT_NEARCAST_SCHEMA = '''
    i message h
        i field h

    message prime_console
        field console_type
        field console_height
        field console_width
    message init

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
    message game_input
        field keycode
'''

class TrackPrimeConsole:
    def __init__(self, orb):
        self.orb = orb
        #
        self.ctype = None
        self.height = None
        self.width = None
    def on_prime_console(self, console_type, console_height, console_width):
        self.ctype = console_type
        self.height = console_height
        self.width = console_width

CONTROL_SCHEME_H_GOLLOP = 'gollop'
CONTROL_SCHEME_H_KEYPAD = 'keypad'
CONTROL_SCHEME_H_VI = 'vi'

CONSOLE_HEIGHT = 28
CONSOLE_WIDTH = 76

GAME_NAME = 'Weed the Garden'

MENU_KEYCODE_NEW_GAME = e_keycode.n
MENU_KEYCODE_CONTINUE = e_keycode.c
MENU_KEYCODE_QUIT = e_keycode.q

ROGUEBOX_ORIGIN_DROP = 0
ROGUEBOX_ORIGIN_REST = 0

ROGUEBOX_GAMEBOX_HEIGHT = CONSOLE_HEIGHT
ROGUEBOX_GAMEBOX_WIDTH = CONSOLE_WIDTH
ROGUEBOX_GAMEBOX_NAIL = (0, 0)
ROGUEBOX_GAMEBOX_PERI = (CONSOLE_HEIGHT, CONSOLE_WIDTH)

ROGUEBOX_MFEED_HEIGHT = CONSOLE_HEIGHT
ROGUEBOX_MFEED_WIDTH = 57
ROGUEBOX_MFEED_NAIL = (0, 23)
ROGUEBOX_MFEED_PERI = (24, 80)

def t100():
    return time.time() * 100

class TrackContainmentMode:
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
        self.track_containment_mode = orb.track(TrackContainmentMode)
        self.d_directive = {}
    def on_quit(self):
        raise SolentQuitException('Quit message on stream')
    def on_directive(self, directive_h, description):
        self.d_directive[directive_h] = description
        #
        if directive_h == 'nw':
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_GOLLOP,
                keycode=e_keycode.q,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_KEYPAD,
                keycode=e_keycode.n7,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_VI,
                keycode=e_keycode.y,
                directive_h=directive_h)
        elif directive_h == 'nn':
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_GOLLOP,
                keycode=e_keycode.w,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_KEYPAD,
                keycode=e_keycode.n8,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_VI,
                keycode=e_keycode.k,
                directive_h=directive_h)
        elif directive_h == 'ne':
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_GOLLOP,
                keycode=e_keycode.e,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_KEYPAD,
                keycode=e_keycode.n9,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_VI,
                keycode=e_keycode.u,
                directive_h=directive_h)
        elif directive_h == 'sw':
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_GOLLOP,
                keycode=e_keycode.z,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_KEYPAD,
                keycode=e_keycode.n1,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_VI,
                keycode=e_keycode.b,
                directive_h=directive_h)
        elif directive_h == 'ss':
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_GOLLOP,
                keycode=e_keycode.x,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_KEYPAD,
                keycode=e_keycode.n2,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_VI,
                keycode=e_keycode.j,
                directive_h=directive_h)
        elif directive_h == 'se':
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_GOLLOP,
                keycode=e_keycode.c,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_KEYPAD,
                keycode=e_keycode.n3,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_VI,
                keycode=e_keycode.n,
                directive_h=directive_h)
        elif directive_h == 'ww':
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_GOLLOP,
                keycode=e_keycode.a,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_KEYPAD,
                keycode=e_keycode.n4,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_VI,
                keycode=e_keycode.h,
                directive_h=directive_h)
        elif directive_h == 'ee':
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_GOLLOP,
                keycode=e_keycode.d,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_KEYPAD,
                keycode=e_keycode.n6,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_VI,
                keycode=e_keycode.l,
                directive_h=directive_h)
        elif directive_h == 'a':
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_GOLLOP,
                keycode=e_keycode.s,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_KEYPAD,
                keycode=e_keycode.n5,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_VI,
                keycode=e_keycode.space,
                directive_h=directive_h)
        elif directive_h == 'b':
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_GOLLOP,
                keycode=e_keycode.r,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_KEYPAD,
                keycode=e_keycode.n0,
                directive_h=directive_h)
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_VI,
                keycode=e_keycode.slash,
                directive_h=directive_h)
        elif directive_h == 'help':
            self.nearcast.keycode_to_directive(
                control_scheme_h=CONTROL_SCHEME_H_VI,
                keycode=e_keycode.qmark,
                directive_h=directive_h)
        else:
            raise Exception('Unhandled directive %s'%(directive.h))
    def on_keystroke(self, keycode):
        if self.track_containment_mode.is_focus_on_menu():
            if keycode in (e_keycode.tab, e_keycode.esc):
                self.b_in_menu = False
                self.nearcast.o_game_focus()
            else:
                self.nearcast.menu_select(
                    menu_keycode=keycode)
        else:
            if keycode in (e_keycode.tab, e_keycode.esc):
                self.b_in_menu = True
                self.nearcast.menu_focus()
            else:
                self.nearcast.game_input(
                    keycode=keycode)

class CogToTerm:
    def __init__(self, cog_h, engine, orb):
        self.cog_h = cog_h
        self.engine = engine
        self.orb = orb
        #
        self.track_prime_console = orb.track(TrackPrimeConsole)
        #
        self.spin_term = None
    def on_init(self):
        self.spin_term = self.engine.init_spin(
            construct=SpinSelectionUi,
            console_type=self.track_prime_console.ctype,
            cb_selui_keycode=self.cb_selui_keycode,
            cb_selui_lselect=self.cb_selui_lselect)
        self.spin_term.disable_selection()
        self.spin_term.open_console(
            width=self.track_prime_console.width,
            height=self.track_prime_console.height)
    def on_term_clear(self):
        self.spin_term.clear()
    def on_term_write(self, drop, rest, s, cpair):
        self.spin_term.write(
            drop=drop,
            rest=rest,
            s=s,
            cpair=cpair)
    #
    def cb_selui_keycode(self, cs_selui_keycode):
        keycode = cs_selui_keycode.keycode
        #
        keycode = e_keycode(keycode)
        self.nearcast.keystroke(
            keycode=keycode)
    def cb_selui_lselect(self, cs_selui_lselect):
        drop = cs_selui_lselect.drop
        rest = cs_selui_lselect.rest
        c = cs_selui_lselect.c
        cpair = cs_selui_lselect.cpair
        #
        pass

class CogToMenu:
    def __init__(self, cog_h, engine, orb):
        self.cog_h = cog_h
        self.engine = engine
        self.orb = orb
        #
        self.track_prime_console = orb.track(TrackPrimeConsole)
        #
        self.rail_menu = RailMenu()
    def on_init(self):
        rail_h = '%s/menu'%(self.cog_h)
        self.rail_menu.zero(
            rail_h=rail_h,
            cb_menu_asks_display_to_clear=self.cb_menu_asks_display_to_clear,
            cb_menu_asks_display_to_write=self.cb_menu_asks_display_to_write,
            cb_menu_selection=self.cb_menu_selection,
            height=self.track_prime_console.height,
            width=self.track_prime_console.width,
            title=GAME_NAME)
        self.rail_menu.add_menu_item(
            menu_keycode=MENU_KEYCODE_NEW_GAME,
            text='new game')
        self.rail_menu.add_menu_item(
            menu_keycode=MENU_KEYCODE_QUIT,
            text='quit')
        self.nearcast.menu_focus()
    def on_menu_focus(self):
        self.rail_menu.render_menu()
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
        if not self.rail_menu.has_menu_keycode(MENU_KEYCODE_CONTINUE):
            self.rail_menu.add_menu_item(
                menu_keycode=MENU_KEYCODE_CONTINUE,
                text='continue')
    #
    def cb_menu_selection(self, cs_menu_selection):
        rail_h = cs_menu_selection.rail_h
        keycode = cs_menu_selection.keycode
        text = cs_menu_selection.text
        #
        self.nearcast.menu_select(
            menu_keycode=keycode)
    def cb_menu_asks_display_to_clear(self, cs_menu_asks_display_to_clear):
        rail_h = cs_menu_asks_display_to_clear.rail_h
        #
        self.nearcast.term_clear()
    def cb_menu_asks_display_to_write(self, cs_menu_asks_display_to_write):
        rail_h = cs_menu_asks_display_to_write.rail_h
        drop = cs_menu_asks_display_to_write.drop
        rest = cs_menu_asks_display_to_write.rest
        s = cs_menu_asks_display_to_write.s
        #
        self.nearcast.term_write(
            drop=drop,
            rest=rest,
            s=s,
            cpair=solent_cpair('blue'))
    #
    def _mi_new_game(self):
        self.nearcast.o_game_new()
        self.nearcast.o_game_focus()
    def _mi_continue(self):
        self.nearcast.o_game_focus()
    def _mi_quit(self):
        raise SolentQuitException()

class CogToRoguebox:
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
        self.track_prime_console = orb.track(TrackPrimeConsole)
        self.track_containment_mode = orb.track(TrackContainmentMode)
        #
        self.rail_roguebox = RailRoguebox()
        self.rail_message_feed = RailMessageFeed()
        self.cgrid_last = None
        self.cgrid_next = None
        self.d_keycode_to_directive = {}
        self.d_control_scheme = {} # (control_scheme_h, directive_h) = keycode
        #
        self.b_game_started = False
        self.b_mail_waiting = False
        self.b_refresh_needed = False
    def orb_turn(self, activity):
        if None == self.rail_roguebox:
            return
        if not self.track_containment_mode.is_focus_on_game():
            return
        if self.b_mail_waiting:
            activity.mark(
                l=self,
                s='mail processing')
            for message in self.rail_roguebox.retrieve_mail():
                self.rail_message_feed.accept(
                    message=message,
                    turn=self.rail_roguebox.get_turn())
            self.b_mail_waiting = False
            self.b_refresh_needed = True
        #
        if self.b_refresh_needed:
            self._diff_display_refresh()
            self.b_refresh_needed = False
    #
    def on_init(self):
        console_height = self.track_prime_console.height
        console_width = self.track_prime_console.width
        #
        if console_height < ROGUEBOX_GAMEBOX_HEIGHT:
            raise Exception("console height %s too small for game height %s."%(
                console_height, ROGUEBOX_GAMEBOX_HEIGHT))
        if console_width < ROGUEBOX_GAMEBOX_WIDTH:
            raise Exception("console width %s too small for game width %s."%(
                console_width, ROGUEBOX_GAMEBOX_WIDTH))
        #
        rail_h = '%s/roguebox'%(self.cog_h)
        self.rail_roguebox.zero(
            rail_h=rail_h,
            engine=self.engine,
            grid_height=ROGUEBOX_GAMEBOX_HEIGHT,
            grid_width=ROGUEBOX_GAMEBOX_WIDTH,
            cb_ready_alert=self._rl_ready_alert,
            cb_grid_alert=self._rl_grid_alert,
            cb_mail_alert=self._rl_mail_alert,
            cb_over_alert=self._rl_over_alert)
        #
        rail_h = '%s/message_feed'%(self.cog_h)
        self.rail_message_feed.zero(
            rail_h=rail_h,
            height=ROGUEBOX_MFEED_HEIGHT,
            width=ROGUEBOX_MFEED_WIDTH,
            cpair_new=solent_cpair('teal'),
            cpair_old=solent_cpair('blue'))
        self.cgrid_last = Cgrid(
            width=console_width,
            height=console_height)
        self.cgrid_next = Cgrid(
            width=console_width,
            height=console_height)
        #
        # sequence the possible directives in the game to the core. this will
        # give this outer core the opportunity to match directives it
        # recognises to keycodes. in the future, you could imagine being able
        # to configure user keystrokes using this data.
        for directive in self.rail_roguebox.get_supported_directives():
            self.nearcast.directive(
                directive_h=directive.h,
                description=directive.description)
    def on_keycode_to_directive(self, control_scheme_h, keycode, directive_h):
        self.d_keycode_to_directive[keycode] = directive_h
        self.d_control_scheme[ (control_scheme_h, directive_h) ] = keycode
    def on_x_game_ready(self):
        self.b_game_started = True
        self.nearcast.o_game_focus()
    def on_o_game_new(self):
        self.rail_message_feed.clear()
        self.rail_roguebox.new_game()
    def on_x_game_mail(self):
        self.b_mail_waiting = True
    def on_x_game_grid(self):
        self.b_refresh_needed = True
    def on_game_input(self, keycode):
        if keycode not in self.d_keycode_to_directive:
            return
        directive_h = self.d_keycode_to_directive[keycode]
        self.rail_roguebox.directive(
            directive_h=directive_h)
        self.rail_message_feed.scroll_past(
            turn=self.rail_roguebox.get_turn()-3)
        self.b_refresh_needed = True
    def on_o_game_focus(self):
        if not self.b_game_started:
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
        self.rail_roguebox.get_cgrid(
            cgrid=self.cgrid_next,
            nail=ROGUEBOX_GAMEBOX_NAIL,
            peri=ROGUEBOX_GAMEBOX_PERI)
        for idx, message in enumerate(self.rail_message_feed.list_messages()):
            self.cgrid_next.put(
                drop=idx,
                rest=0,
                s=message,
                cpair=solent_cpair('white'))
        #
        for drop in range(self.track_prime_console.height):
            for rest in range(self.track_prime_console.width):
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


# --------------------------------------------------------
#   bootstrap
# --------------------------------------------------------
MTU = 1500

def get_broadcast():
    if platform.system() == 'Darwin':
        return '127.0.0.1'
    else:
        return '127.255.255.255'

def main():
    console_type = 'curses'
    init_network_logging(
        mtu=1490,
        addr=get_broadcast(),
        port=4999,
        label=__name__)
    log("Log opened.")

    engine = None
    try:
        engine = Engine(
            mtu=MTU)
        engine.set_default_timeout(0.04)
        #engine.debug_eloop_on()
        #
        orb = engine.init_orb(
            i_nearcast=I_CONTAINMENT_NEARCAST_SCHEMA)
        orb.add_log_snoop()
        orb.init_cog(CogInterpreter)
        orb.init_cog(CogToTerm)
        orb.init_cog(CogToMenu)
        orb.init_cog(CogToRoguebox)
        #
        bridge = orb.init_autobridge()
        bridge.nearcast.prime_console(
            console_type=console_type,
            console_height=CONSOLE_HEIGHT,
            console_width=CONSOLE_WIDTH)
        bridge.nearcast.init()
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

