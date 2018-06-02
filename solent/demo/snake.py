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

from solent import Engine
from solent import e_keycode
from solent import init_network_logging
from solent import log
from solent import ns
from solent import solent_cpair
from solent import SolentQuitException
from solent import uniq

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
#   game model
# --------------------------------------------------------
def create_spot(drop, rest):
    return (drop, rest)

MAX_EGG_LIFE = 60

class Board:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        #
        self.game_over = False
        self.egg_life = 0
        #
        self.wall_spots = []
        self.free_spots = []
        self.egg_spots = []
        self.snake_spots = deque()
        #
        self._create_free_spots()
        self._create_barrier()
        self._create_snake()
        self._create_egg()
    #
    def is_game_over(self):
        return self.game_over
    def tick_n(self):
        if self.game_over:
            raise Exception("game is over")
        (drop, rest) = self.snake_spots[-1]
        drop -= 1
        self._handle_movement(
            drop=drop,
            rest=rest)
    def tick_w(self):
        if self.game_over:
            raise Exception("game is over")
        (drop, rest) = self.snake_spots[-1]
        rest -= 1
        self._handle_movement(
            drop=drop,
            rest=rest)
    def tick_e(self):
        if self.game_over:
            raise Exception("game is over")
        (drop, rest) = self.snake_spots[-1]
        rest += 1
        self._handle_movement(
            drop=drop,
            rest=rest)
    def tick_s(self):
        if self.game_over:
            raise Exception("game is over")
        (drop, rest) = self.snake_spots[-1]
        drop += 1
        self._handle_movement(
            drop=drop,
            rest=rest)
    #
    def _create_free_spots(self):
        for drop in range(self.height):
            for rest in range(self.width):
                self.free_spots.append( create_spot(drop, rest) )
    def _create_barrier(self):
        for rest in range(self.width):
            spot = (0, rest)
            self.free_spots.remove(spot)
            self.wall_spots.append(spot)
            spot = (self.height-1, rest)
            self.free_spots.remove(spot)
            self.wall_spots.append(spot)
        for drop in range(self.height-2):
            spot = (drop+1, 0)
            self.free_spots.remove(spot)
            self.wall_spots.append(spot)
            spot = (drop+1, self.width-1)
            self.free_spots.remove(spot)
            self.wall_spots.append(spot)
    def _create_snake(self):
        (drop, rest) = (int(self.height/2), int(self.width/4))
        #
        # tail segment
        spot = create_spot(drop, rest)
        self.free_spots.remove(spot)
        self.snake_spots.appendleft(spot)
        rest -= 1
        spot = create_spot(drop, rest)
        self.free_spots.remove(spot)
        self.snake_spots.appendleft(spot)
        rest -= 1
        spot = create_spot(drop, rest)
        self.free_spots.remove(spot)
        self.snake_spots.appendleft(spot)
        rest -= 1
    def _create_egg(self):
        spot = random.choice(self.free_spots)
        self.egg_spots.append(spot)
        self.free_spots.remove(spot)
        self.egg_life = 0
    def _egg_rotation(self):
        # for the moment, just create a new one
        #
        # Remove the current egg
        if self.egg_spots:
            self.free_spots.append(
                self.egg_spots.pop())
        self._create_egg()
    def _handle_movement(self, drop, rest):
        spot = create_spot(drop, rest)
        if self.game_over:
            raise Exception('game is over')
        #
        if spot in self.egg_spots:
            # snake grows
            self.egg_spots.remove(spot)
            self.snake_spots.append(spot)
            self._create_egg()
        elif spot in self.free_spots:
            # snake shuffles
            self.free_spots.remove(spot)
            self.snake_spots.append(spot)
            self.free_spots.append(
                self.snake_spots.popleft())
        else:
            self.game_over = True
        #
        self.egg_life += 1
        if self.egg_life > MAX_EGG_LIFE:
            self._egg_rotation()
            self.egg_life = 0

SPOT_SNAKE_CAR = '@'
SPOT_SNAKE_CDR = 'x'
SPOT_EGG = 'O'

class RailSnakeGame:
    def __init__(self):
        self.cs_game_instructs_clear = ns()
        self.cs_game_instructs_write = ns()
        #
        self.b_running = False
    def call_game_instructs_clear(self, rail_h):
        self.cs_game_instructs_clear.rail_h = rail_h
        self.cb_game_instructs_clear(
            cs_game_instructs_clear=self.cs_game_instructs_clear)
    def call_game_instructs_write(self, rail_h, drop, rest, s, cpair):
        self.cs_game_instructs_write.rail_h = rail_h
        self.cs_game_instructs_write.drop = drop
        self.cs_game_instructs_write.rest = rest
        self.cs_game_instructs_write.s = s
        self.cs_game_instructs_write.cpair = cpair
        self.cb_game_instructs_write(
            cs_game_instructs_write=self.cs_game_instructs_write)
    def zero(self, rail_h, height, width, cb_game_instructs_clear, cb_game_instructs_write):
        self.rail_h = rail_h
        self.height = height
        self.width = width
        self.cb_game_instructs_clear = cb_game_instructs_clear
        self.cb_game_instructs_write = cb_game_instructs_write
        #
        self.b_running = True
        #
        self.board = Board(
            height=height,
            width=width)
        #
        # this is a list so we can effectively ignore conflicting keystrokes.
        # (Avoiding the player from turning back on themselves in the same
        # space is more of a problem than I first expected.)
        self.snake_direction = 'e'
        self.steer_orders = deque()
    def tick(self):
        if self.board.is_game_over():
            return
        #
        if self.steer_orders:
            self.snake_direction = self.steer_orders.popleft()
        #
        if self.snake_direction == 'e':
            self.board.tick_e()
        if self.snake_direction == 'w':
            self.board.tick_w()
        if self.snake_direction == 's':
            self.board.tick_s()
        if self.snake_direction == 'n':
            self.board.tick_n()
        #
        self.render()
    def steer(self, cardinal):
        if len(cardinal) != 1 or cardinal not in 'nsew':
            raise Exception('invalid cardinal %s'%(cardinal))
        #
        # can't go back on yourself
        if self.steer_orders:
            last_move = self.steer_orders[-1]
        else:
            last_move = self.snake_direction
        if last_move == 'n' and cardinal == 's':
            return
        if last_move == 's' and cardinal == 'n':
            return
        if last_move == 'w' and cardinal == 'e':
            return
        if last_move == 'e' and cardinal == 'w':
            return
        #
        self.steer_orders.append(cardinal)
    def render(self):
        self.call_game_instructs_clear(
            rail_h=self.rail_h)
        for spot in self.board.wall_spots:
            (drop, rest) = spot
            self.call_game_instructs_write(
                rail_h=self.rail_h,
                drop=drop,
                rest=rest,
                s='.',
                cpair=solent_cpair('orange'))
        for spot in self.board.egg_spots:
            (drop, rest) = spot
            self.call_game_instructs_write(
                rail_h=self.rail_h,
                drop=drop,
                rest=rest,
                s='O',
                cpair=solent_cpair('yellow'))
        #
        if self.board.is_game_over():
            cpair = solent_cpair('red')
        else:
            cpair = solent_cpair('green')
        #
        for spot in self.board.snake_spots:
            (drop, rest) = spot
            self.call_game_instructs_write(
                rail_h=self.rail_h,
                drop=drop,
                rest=rest,
                s='O',
                cpair=cpair)
        # replace the head with a new character
        self.call_game_instructs_write(
            rail_h=self.rail_h,
            drop=drop,
            rest=rest,
            s='X',
            cpair=cpair)


# --------------------------------------------------------
#   nearcast model
# --------------------------------------------------------
#
# Containment consists of a menu system, a terminal, and a cog that
# encapsulates the game.
#
I_NEARCAST = '''
    i schema h
    i message h
    i field h

    schema nc.snake

    message prime_console
        field console_type
        field height
        field width
    message prime_menu_title
        field text
    message init

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
    message menu_select
        field menu_keycode
'''

class TrackPrimeConsole:
    def __init__(self, orb):
        self.orb = orb
    def on_prime_console(self, console_type, height, width):
        self.console_type = console_type
        self.height = height
        self.width = width

class TrackPrimeMenuTitle:
    def __init__(self, orb):
        self.orb = orb
    def on_prime_menu_title(self, text):
        self.text = text

MENU_KEYCODE_NEW_GAME = e_keycode.n
MENU_KEYCODE_CONTINUE = e_keycode.c
MENU_KEYCODE_QUIT = e_keycode.q

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
        self.track_containment_mode = orb.track(TrackContainmentMode)
    def on_keystroke(self, keycode):
        if self.track_containment_mode.is_focus_on_menu():
            if keycode == e_keycode.tab:
                self.b_in_menu = False
                self.nearcast.game_focus()
            else:
                self.nearcast.menu_select(
                    menu_keycode=keycode)
        else:
            if keycode == e_keycode.tab:
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
        self.track_prime_console = orb.track(TrackPrimeConsole)
        #
        self.spin_term = None
    #
    def on_init(self):
        self.spin_term = self.engine.init_spin(
            construct=SpinSelectionUi,
            console_type=self.track_prime_console.console_type,
            cb_selui_keycode=self.cb_selui_keycode,
            cb_selui_lselect=self.cb_selui_lselect)
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
        log('xxx cb_selui_lselect drop %s rest %s c %s cpair %s'%(drop, rest, c, cpair))

class CogToMenu:
    def __init__(self, cog_h, engine, orb):
        self.cog_h = cog_h
        self.engine = engine
        self.orb = orb
        #
        self.track_prime_console = self.orb.track(TrackPrimeConsole)
        self.track_prime_menu_title = self.orb.track(TrackPrimeMenuTitle)
        #
        self.rail_menu = RailMenu()
    def on_init(self):
        rail_h = '%s/menu'%(self.cog_h)
        self.rail_menu.zero(
            rail_h=rail_h,
            cb_menu_selection=self.cb_menu_selection,
            cb_menu_asks_display_to_clear=self.cb_menu_asks_display_to_clear,
            cb_menu_asks_display_to_write=self.cb_menu_asks_display_to_write,
            height=self.track_prime_console.height,
            width=self.track_prime_console.width,
            title=self.track_prime_menu_title.text)
        #
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
    def on_game_new(self):
        if not self.rail_menu.has_menu_keycode(MENU_KEYCODE_CONTINUE):
            self.rail_menu.add_menu_item(
                menu_keycode=MENU_KEYCODE_CONTINUE,
                text='continue')
    #
    def cb_menu_selection(self, cs_menu_selection):
        rail_h = cs_menu_selection.rail_h
        keycode = cs_menu_selection.keycode
        #
        self.nearcast.menu_select(
            menu_keycode=keycode)
    def cb_menu_asks_display_to_clear(self, cs_menu_asks_display_to_clear):
        self.nearcast.term_clear()
    def cb_menu_asks_display_to_write(self, cs_menu_asks_display_to_write):
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
        self.nearcast.game_new()
        self.nearcast.game_focus()
    def _mi_continue(self):
        self.nearcast.game_focus()
    def _mi_quit(self):
        raise SolentQuitException()

class CogSnakeGame:
    def __init__(self, cog_h, engine, orb):
        self.cog_h = cog_h
        self.engine = engine
        self.orb = orb
        #
        self.track_containment_mode = orb.track(TrackContainmentMode)
        self.track_prime_console = orb.track(TrackPrimeConsole)
        #
        self.rail_snake_game = RailSnakeGame()
        #
        self.tick_t100 = None
    def orb_turn(self, activity):
        if self.rail_snake_game == None:
            return
        if not self.track_containment_mode.is_focus_on_game():
            return
        now_t100 = t100()
        if now_t100 - self.tick_t100 > 6:
            activity.mark(self, 'game tick')
            self.rail_snake_game.tick()
            self.tick_t100 = now_t100
    #
    def on_init(self):
        pass
    def on_game_new(self):
        rail_h = '%s/snake_game'%(self.cog_h)
        self.rail_snake_game.zero(
            rail_h=rail_h,
            height=self.track_prime_console.height,
            width=self.track_prime_console.width,
            cb_game_instructs_clear=self.cb_game_instructs_clear,
            cb_game_instructs_write=self.cb_game_instructs_write)
    def on_game_input(self, keycode):
        if keycode == e_keycode.a:
            self.rail_snake_game.steer(
                cardinal='w')
        elif keycode == e_keycode.w:
            self.rail_snake_game.steer(
                cardinal='n')
        elif keycode == e_keycode.d:
            self.rail_snake_game.steer(
                cardinal='e')
        elif keycode in (e_keycode.x, e_keycode.s):
            self.rail_snake_game.steer(
                cardinal='s')
    def on_game_focus(self):
        self.tick_t100 = t100()
        #
        # We cannot switch to game focus until it after its first start.
        if not self.rail_snake_game.b_running:
            self.nearcast.menu_focus()
            return
        #
        self.rail_snake_game.render()
    #
    def cb_game_instructs_clear(self, cs_game_instructs_clear):
        self.nearcast.term_clear()
    def cb_game_instructs_write(self, cs_game_instructs_write):
        drop = cs_game_instructs_write.drop
        rest = cs_game_instructs_write.rest
        s = cs_game_instructs_write.s
        cpair = cs_game_instructs_write.cpair
        #
        self.nearcast.term_write(
            drop=drop,
            rest=rest,
            s=s,
            cpair=cpair)

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

def init_nearcast(engine, console_type):
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST)
    orb.init_cog(CogInterpreter)
    orb.init_cog(CogTerm)
    orb.init_cog(CogToMenu)
    orb.init_cog(CogSnakeGame)
    #
    bridge = orb.init_cog(CogBridge)
    bridge.nearcast.prime_console(
        console_type=console_type,
        height=24,
        width=78)
    bridge.nearcast.prime_menu_title(
        text=GAME_NAME)
    bridge.nearcast.init()
    #
    return bridge


# --------------------------------------------------------
#   bootstrap
# --------------------------------------------------------
GAME_NAME = 'snake'

MTU = 1500

def main():
    console_type = 'curses'
    if '--pygame' in sys.argv:
        console_type = 'pygame'
    elif sys.platform in ('msys', 'win32', 'win64'):
        b_ok = True
        try:
            import pygame
            console_type = 'pygame'
        except:
            print("[!] On Windows, snake needs pygame. (But, try winsnake!).")
            sys.exit(1)
    #
    engine = Engine(
        mtu=MTU)
    try:
        engine.default_timeout = 0.01
        init_nearcast(
            engine=engine,
            console_type=console_type)
        #
        engine.event_loop()
    except SolentQuitException:
        pass
    finally:
        engine.close()

if __name__ == '__main__':
    main()

