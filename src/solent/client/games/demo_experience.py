#!/usr/bin/python
#
# Intends to demonstrate basic use of the experience class
#

from .turnlib.rogue_console import rogue_console_new
from .turnlib.gollop_console import gollop_console_new
from .turnlib.menu import menu_new
from .turnlib.fabric import fabric_new_grid

from solent.client.constants import *
from solent.client.term.cgrid import cgrid_new
from solent.client.term.meep import meep_new
from solent.client.term.curses_term import curses_term_start, curses_term_end
from solent.client.term.window_term import window_term_start, window_term_end
from solent.exceptions import SolentQuitException
from solent.util import uniq

import os
import sys
import traceback

C_GAME_WIDTH = 78
C_GAME_HEIGHT = 25

TITLE = '[demo_experience]'


# --------------------------------------------------------
#   :experience_console
# --------------------------------------------------------
#
# Responsible for displaying a menu, and exposing interaction points with it.
# This acts as a pipeline for keyboard input and display events. Where the
# game is running, it just passes the events through to the game.
#
CPAIR_MENU_BORDER = SOL_CPAIR_BLACK_CYAN
CPAIR_MENU_TEXT = SOL_CPAIR_T_WHITE
CPAIR_TITLE = SOL_CPAIR_T_WHITE

class ExperienceConsole(object):
    def __init__(self, title, console):
        '''
        cgrid
            the memory to be used for rendering activity
        title
            to display on the console
        menu
            instance of menu class that the user interacts with through
            this console
        '''
        self.title = title
        self.console = console
        #
        # no harm reusing it
        self.cgrid = self.console.cgrid
        self.b_in_game = False
        #
        self.menu = self.__init_menu()
        self.__init_menu()
        #
        self.title_cgrid = None
        self.__init_title()
        #
        self.menu_cgrid = None
        self.__init_menu_grid()
    def __init_menu(self):
        menu = menu_new()
        menu.add('c', 'continue', self.mi_continue_game)
        menu.add('n', 'new', self.mi_new_game)
        menu.add('l', 'load', self.mi_load_game)
        menu.add('s', 'save', self.mi_save_game)
        menu.add('q', 'quit', self.mi_quit)
        return menu
    def __init_title(self):
        # Later on we could use something like pyfiglet for this. Better would
        # be a single distinct font, similar to what Gollop did with rebelstar.
        self.title_cgrid = cgrid_new(
            width=len(self.title),
            height=1)
        self.title_cgrid.put(
            drop=0,
            rest=0,
            s=self.title,
            cpair=CPAIR_TITLE)
    def __init_menu_grid(self):
        lines = self.menu.get_lines()
        longest_line = 0
        for l in lines:
            longest_line = max( [longest_line, len(l)] )
        #
        # prepare the menu border
        self.menu_cgrid = cgrid_new(
            width=longest_line+4,
            height=len(lines)+2)
        horiz = ' '*(longest_line+4)
        blank = ' '*(longest_line+4)
        menu_border_height = len(lines)+2
        for idx in range(menu_border_height):
            if idx in (0, menu_border_height-1):
                self.menu_cgrid.put(
                    drop=idx,
                    rest=0,
                    s=horiz,
                    cpair=CPAIR_MENU_BORDER)
            else:
                line = lines[idx-1]
                self.menu_cgrid.put(
                    drop=idx,
                    rest=0,
                    s=' ',
                    cpair=CPAIR_MENU_BORDER)
                self.menu_cgrid.put(
                    drop=idx,
                    rest=1,
                    s=' %s%s '%(line, ' '*(longest_line-len(line))),
                    cpair=CPAIR_MENU_TEXT)
                self.menu_cgrid.put(
                    drop=idx,
                    rest=longest_line+3,
                    s=' ',
                    cpair=CPAIR_MENU_BORDER)
    def _redraw_title(self):
        self.cgrid.blit(
            src_cgrid=self.title_cgrid,
            nail=(0, 0))
    def _redraw_menu(self):
        menu_drop = int((self.cgrid.height / 2) - (self.menu_cgrid.height / 2))
        menu_rest = int((self.cgrid.width / 2) - (self.menu_cgrid.width / 2))
        nail = (menu_drop, menu_rest)
        self.cgrid.blit(
            src_cgrid=self.menu_cgrid,
            nail=nail)
    #
    def to_menu(self):
        self.b_in_game = False
    def mi_continue_game(self):
        self.b_in_game = True
    def mi_new_game(self):
        print('xxx new game')
        self.b_in_game = True
    def mi_load_game(self):
        print('xxx mi_load_game')
    def mi_save_game(self):
        print('xxx mi_save_game')
    def mi_quit(self):
        raise SolentQuitException()
    #
    def accept(self, key):
        if '' == key:
            return
        elif ord(key) == 27 and self.b_in_game:
            self.to_menu()
        elif ord(key) == 27:
            self.b_in_game = True
        elif self.b_in_game:
            self.console.accept(
                key=key)
        else:
            if not self.menu.has_key(key):
                return
            fn = self.menu.get_callback(key)
            fn()
    def redraw(self, grid_display):
        if self.b_in_game:
            self.console.redraw(
                grid_display=grid_display)
        else:
            self._redraw_title()
            self._redraw_menu()
            grid_display.update(
                cgrid=self.cgrid)

def experience_console_new(title, console):
    ob = ExperienceConsole(
        title=title,
        console=console)
    return ob


# --------------------------------------------------------
#   :console_regulator
# --------------------------------------------------------
class ConsoleRegulator(object):
    def __init__(self, keystream, grid_display, console):
        self.keystream = keystream
        self.grid_display = grid_display
        self.console = console
    def run_event_loop(self):
        # draw instructions
        #
        self.console.redraw(self.grid_display)
        while True:
            self.console.accept(
                key=self.keystream.next())
            self.console.redraw(self.grid_display)

def console_regulator_new(keystream, grid_display, console):
    ob = ConsoleRegulator(
        keystream=keystream,
        grid_display=grid_display,
        console=console)
    return ob


# --------------------------------------------------------
#   :gollop_game
# --------------------------------------------------------
class GollopGame(object):
    def __init__(self):
        self._meeps = [
            meep_new(
                s=0,
                e=0,
                c='O',
                cpair=SOL_CPAIR_WHITE_T)
        ]
        self._cursor = self._meeps[0]
        self.fabric = fabric_new_grid()
    def get_cursor(self):
        return self._cursor
    def get_meeps(self):
        return self._meeps
    def gollop_cursor_move_nw(self):
        self._cursor.s += -1
        self._cursor.e += -1
    def gollop_cursor_move_nn(self):
        self._cursor.s += -1
        self._cursor.e += 0
    def gollop_cursor_move_ne(self):
        self._cursor.s += -1
        self._cursor.e += 1
    def gollop_cursor_move_ww(self):
        self._cursor.s += 0
        self._cursor.e += -1
    def gollop_cursor_move_ee(self):
        self._cursor.s += 0
        self._cursor.e += 1
    def gollop_cursor_move_sw(self):
        self._cursor.s += 1
        self._cursor.e += -1
    def gollop_cursor_move_ss(self):
        self._cursor.s += 1
        self._cursor.e += 0
    def gollop_cursor_move_se(self):
        self._cursor.s += 1
        self._cursor.e += 1
    def gollop_cursor_select(self):
        print('xxx gollop_select')

def gollop_game_new():
    ob = GollopGame()
    return ob


# --------------------------------------------------------
#   :rogue_game
# --------------------------------------------------------
class RogueGame(object):
    def __init__(self, player):
        self.player = player
        self.fabric = fabric_new_grid()
        #
        self._meeps = []
        self._meeps.append(
            meep_new(
                s=0,
                e=0,
                c='<',
                cpair=SOL_CPAIR_WHITE_T))
        self._meeps.append(
            meep_new(
                s=-2,
                e=-2,
                c='|',
                cpair=SOL_CPAIR_WHITE_T))
        self._meeps.append(
            meep_new(
                s=-3,
                e=0,
                c='|',
                cpair=SOL_CPAIR_WHITE_T))
        self._meeps.append(
            meep_new(
                s=-2,
                e=2,
                c='|',
                cpair=SOL_CPAIR_WHITE_T))
        self._meeps.append(
            meep_new(
                s=0,
                e=-3,
                c='|',
                cpair=SOL_CPAIR_WHITE_T))
        self._meeps.append(
            meep_new(
                s=0,
                e=3,
                c='|',
                cpair=SOL_CPAIR_WHITE_T))
        self._meeps.append(
            meep_new(
                s=2,
                e=-2,
                c='|',
                cpair=SOL_CPAIR_WHITE_T))
        self._meeps.append(
            meep_new(
                s=3,
                e=0,
                c='|',
                cpair=SOL_CPAIR_WHITE_T))
        self._meeps.append(
            meep_new(
                s=2,
                e=2,
                c='|',
                cpair=SOL_CPAIR_WHITE_T))
        self._meeps.append(self.player)
    def get_meeps(self):
        return self._meeps
    def move_nw(self, meep):
        meep.s += -1
        meep.e += -1
    def move_nn(self, meep):
        meep.s += -1
        meep.e += 0
    def move_ne(self, meep):
        meep.s += -1
        meep.e += 1
    def move_ww(self, meep):
        meep.s += 0
        meep.e += -1
    def move_ee(self, meep):
        meep.s += 0
        meep.e += 1
    def move_sw(self, meep):
        meep.s += 1
        meep.e += -1
    def move_ss(self, meep):
        meep.s += 1
        meep.e += 0
    def move_se(self, meep):
        meep.s += 1
        meep.e += 1

def rogue_game_new():
    player = meep_new(
        s=0,
        e=0,
        c='@',
        cpair=SOL_CPAIR_RED_T)
    #
    ob = RogueGame(
        player=player)
    return ob


# --------------------------------------------------------
#   :alg
# --------------------------------------------------------
def main():
    if '--tty' in sys.argv:
        fn_device_start = curses_term_start
        fn_device_end = curses_term_end
    elif '--win' in sys.argv:
        fn_device_start = window_term_start
        fn_device_end = window_term_end
    else:
        print('ERROR: specify --tty or --win')
        sys.exit(1)
    try:
        rogue_game = rogue_game_new()
        rogue_console = rogue_console_new(
            rogue_game=rogue_game,
            width=C_GAME_WIDTH,
            height=C_GAME_HEIGHT)
        '''
        gollop_game = gollop_game_new()
        gollop_console = gollop_console_new(
            gollop_game=gollop_game,
            width=C_GAME_WIDTH,
            height=C_GAME_HEIGHT)
        '''
        #
        experience_console = experience_console_new(
            title=TITLE,
            console=rogue_console)
            #console=gollop_console)
        #
        term_shape = fn_device_start(
            game_width=C_GAME_WIDTH,
            game_height=C_GAME_HEIGHT)
        console_regulator = console_regulator_new(
            keystream=term_shape.get_keystream(),
            grid_display=term_shape.get_grid_display(),
            console=experience_console)
        console_regulator.run_event_loop()
    except SolentQuitException:
        pass
    except:
        traceback.print_exc()
    finally:
        fn_device_end()

if __name__ == '__main__':
    main()

