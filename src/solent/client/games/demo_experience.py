#!/usr/bin/python
#
# Intends to demonstrate basic use of the experience class
#

from .turnlib.experience_console import experience_console_new
from .turnlib.rogue_console import rogue_console_new
from .turnlib.gollop_console import gollop_console_new
from .turnlib.rogue_plane import rogue_plane_new

from solent.client.constants import *
from solent.client.term.cgrid import cgrid_new
from solent.client.term.cursor import cursor_new
from solent.client.term.curses_term import curses_term_start, curses_term_end
from solent.client.term.perspective import perspective_new
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
#   :rogue_game
# --------------------------------------------------------
class RogueGame(object):
    def __init__(self, rogue_plane, player_meep):
        self.rogue_plane = rogue_plane
        self.player_meep = player_meep

def rogue_game_new(rogue_plane, player_meep):
    ob = RogueGame(
        rogue_plane=rogue_plane,
        player_meep=player_meep)
    return ob


# --------------------------------------------------------
#   :alg
# --------------------------------------------------------
def prep_plane(rogue_plane):
    rogue_plane.create_meep(
        s=0,
        e=0,
        c='<',
        cpair=SOL_CPAIR_WHITE_T)
    rogue_plane.create_meep(
        s=-2,
        e=-2,
        c='|',
        cpair=SOL_CPAIR_WHITE_T)
    rogue_plane.create_meep(
        s=-3,
        e=0,
        c='|',
        cpair=SOL_CPAIR_WHITE_T)
    rogue_plane.create_meep(
        s=-2,
        e=2,
        c='|',
        cpair=SOL_CPAIR_WHITE_T)
    rogue_plane.create_meep(
        s=0,
        e=-3,
        c='|',
        cpair=SOL_CPAIR_WHITE_T)
    rogue_plane.create_meep(
        s=0,
        e=3,
        c='|',
        cpair=SOL_CPAIR_WHITE_T)
    rogue_plane.create_meep(
        s=2,
        e=-2,
        c='|',
        cpair=SOL_CPAIR_WHITE_T)
    rogue_plane.create_meep(
        s=3,
        e=0,
        c='|',
        cpair=SOL_CPAIR_WHITE_T)
    rogue_plane.create_meep(
        s=2,
        e=2,
        c='|',
        cpair=SOL_CPAIR_WHITE_T)

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
        rogue_plane = rogue_plane_new()
        prep_plane(
            rogue_plane=rogue_plane)
        #
        player_meep = rogue_plane.create_meep(
            s=0,
            e=0,
            c='@',
            cpair=SOL_CPAIR_RED_T)
        rogue_game = rogue_game_new(
            rogue_plane=rogue_plane,
            player_meep=player_meep)
        #
        cursor = cursor_new(
            fn_s=lambda: player_meep.s,
            fn_e=lambda: player_meep.e,
            fn_c=lambda: player_meep.c,
            fn_cpair=lambda: player_meep.cpair)
        perspective = perspective_new(
            cursor=cursor,
            width=C_GAME_WIDTH,
            height=C_GAME_HEIGHT)
        rogue_console = rogue_console_new(
            rogue_game=rogue_game,
            perspective=perspective)
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

