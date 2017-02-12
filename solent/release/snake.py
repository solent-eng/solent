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

from solent import solent_cpair
from solent import solent_keycode
from solent import uniq
from solent.brick import brick_menu_new
from solent.eng import engine_new
from solent.exceptions import SolentQuitException
from solent.log import init_logging
from solent.log import log
from solent.term import spin_term_new

from collections import deque
import os
import random
import sys
import time
import traceback

GAME_NAME = 'snake'

MTU = 1500


# --------------------------------------------------------
#   :game
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

class SpinSnakeGame:
    def __init__(self, height, width, cb_display_clear, cb_display_write):
        self.height = height
        self.width = width
        self.cb_display_clear = cb_display_clear
        self.cb_display_write = cb_display_write
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
        self.cb_display_clear()
        for spot in self.board.wall_spots:
            (drop, rest) = spot
            self.cb_display_write(
                drop=drop,
                rest=rest,
                s='.',
                cpair=solent_cpair('orange'))
        for spot in self.board.egg_spots:
            (drop, rest) = spot
            self.cb_display_write(
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
            self.cb_display_write(
                drop=drop,
                rest=rest,
                s='O',
                cpair=cpair)
        # replace the head with a new character
        self.cb_display_write(
            drop=drop,
            rest=rest,
            s='X',
            cpair=cpair)

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

MENU_KEYCODE_NEW_GAME = solent_keycode('n')
MENU_KEYCODE_CONTINUE = solent_keycode('c')
MENU_KEYCODE_QUIT = solent_keycode('q')

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
        self.track_containment_mode = orb.init_track(TrackContainmentMode)
    def on_quit(self):
        raise SolentQuitException('Quit message on stream')
    def on_keystroke(self, keycode):
        if self.track_containment_mode.is_focus_on_menu():
            if keycode == solent_keycode('tab'):
                self.b_in_menu = False
                self.nearcast.game_focus()
            else:
                self.nearcast.menu_select(
                    menu_keycode=keycode)
        else:
            if keycode == solent_keycode('tab'):
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
    def at_turn(self, activity):
        if None == self.spin_term:
            return
        self.spin_term.at_turn(
            activity=activity)
    #
    def on_init(self, console_type, height, width):
        self.spin_term = self.engine.init_spin(
            construct=spin_term_new,
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

class CogMenu:
    def __init__(self, cog_h, engine, orb):
        self.cog_h = cog_h
        self.engine = engine
        self.orb = orb
        #
        self.brick_menu = None
    def on_init(self, console_type, height, width):
        self.brick_menu = brick_menu_new(
            height=height,
            width=width,
            cb_display_clear=self.menu_display_clear,
            cb_display_write=self.menu_display_write)
        self.nearcast.menu_title(
            text=GAME_NAME)
        self.nearcast.menu_item(
            menu_keycode=MENU_KEYCODE_NEW_GAME,
            text='new game')
        self.nearcast.menu_item(
            menu_keycode=MENU_KEYCODE_QUIT,
            text='quit')
        self.nearcast.menu_focus()
    def on_menu_title(self, text):
        self.brick_menu.set_title(
            text=text)
    def on_menu_item(self, menu_keycode, text):
        self.brick_menu.add_menu_item(
            menu_keycode=menu_keycode,
            text=text,
            cb_select=lambda: self.menu_select(
                menu_keycode=keycode))
    def on_menu_focus(self):
        self.brick_menu.render_menu()
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
        if not self.brick_menu.has_menu_keycode(MENU_KEYCODE_CONTINUE):
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
        self.track_containment_mode = orb.init_track(TrackContainmentMode)
        self.height = None
        self.width = None
        self.spin_snake_game = None
        self.tick_t100 = None
    def at_turn(self, activity):
        if self.spin_snake_game == None:
            return
        if not self.track_containment_mode.is_focus_on_game():
            return
        now_t100 = t100()
        if now_t100 - self.tick_t100 > 6:
            activity.mark(self, 'game tick')
            self.spin_snake_game.tick()
            self.tick_t100 = now_t100
    #
    def on_init(self, console_type, height, width):
        self.height = height
        self.width = width
    def on_game_new(self):
        self.spin_snake_game = spin_snake_game_new(
            height=self.height,
            width=self.width,
            cb_display_clear=self.game_display_clear,
            cb_display_write=self.game_display_write)
    def on_game_input(self, keycode):
        if keycode == solent_keycode('a'):
            self.spin_snake_game.steer(
                cardinal='w')
        elif keycode == solent_keycode('w'):
            self.spin_snake_game.steer(
                cardinal='n')
        elif keycode == solent_keycode('d'):
            self.spin_snake_game.steer(
                cardinal='e')
        elif keycode == solent_keycode('x'):
            self.spin_snake_game.steer(
                cardinal='s')
    def on_game_focus(self):
        self.tick_t100 = t100()
        if None == self.spin_snake_game:
            self.nearcast.menu_focus()
            return
        self.spin_snake_game.render()
    #
    def game_display_clear(self):
        self.nearcast.term_clear()
    def game_display_write(self, drop, rest, s, cpair):
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

def game(console_type):
    init_logging()
    #
    engine = None
    try:
        engine = engine_new(
            mtu=MTU)
        engine.default_timeout = 0.01
        #
        orb = engine.init_orb(
            spin_h=__name__,
            i_nearcast=I_CONTAINMENT_NEARCAST_SCHEMA)
        orb.init_cog(CogInterpreter)
        orb.init_cog(CogTerm)
        orb.init_cog(CogMenu)
        orb.init_cog(CogSnakeGame)
        #
        bridge = orb.init_cog(CogBridge)
        bridge.nc_init(
            console_type=console_type,
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

def main():
    if '--curses' in sys.argv:
        console_type = 'curses'
    elif '--pygame' in sys.argv:
        console_type = 'pygame'
    else:
        print('ERROR: specify either --curses or --pygame')
        sys.exit(1)
    game(
        console_type=console_type)

if __name__ == '__main__':
    main()

