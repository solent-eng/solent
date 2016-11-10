#!/usr/bin/python
#
# Intends to demonstrate basic use of the experience class
#

from .turnlib.experience_console import experience_console_new
from .turnlib.rogue_console import rogue_console_new
from .turnlib.rogue_plane import rogue_plane_new
from .turnlib.time_system import time_system_new

from solent.client.constants import *
from solent.client.term.cgrid import cgrid_new
from solent.client.term.cursor import cursor_new
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
#   :io_regulator
# --------------------------------------------------------
class TurnBasedEventLoop(object):
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

def turn_based_event_loop_new(keystream, grid_display, console):
    ob = TurnBasedEventLoop(
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
#   :boxes
# --------------------------------------------------------
BOX_LINE = uniq()
BOX_EDGE = uniq()
BOX_VOID = uniq()
BOX_HASH = uniq()
BOX_STOP = uniq()

def make_box(rogue_plane, se_nail, width, height, cpair=SOL_CPAIR_WHITE_T, box_type=BOX_LINE):
    '''
    Box type indicates the kind of corners the box should have.
    '''
    (s_nail, e_nail) = se_nail
    hori = width+2
    for i in range(hori):
        if (i, box_type) in [(0, BOX_EDGE), (hori-1, BOX_VOID)]:
            rogue_plane.create_terrain(
                s=s_nail,
                e=e_nail+i,
                c='/',
                cpair=cpair)
            rogue_plane.create_terrain(
                s=s_nail+height+1,
                e=e_nail+i,
                c='\\',
                cpair=cpair)
        elif (i, box_type) in [(hori-1, BOX_EDGE), (0, BOX_VOID)]:
            rogue_plane.create_terrain(
                s=s_nail,
                e=e_nail+i,
                c='\\',
                cpair=cpair)
            rogue_plane.create_terrain(
                s=s_nail+height+1,
                e=e_nail+i,
                c='/',
                cpair=cpair)
        else:
            if box_type == BOX_HASH:
                c = '#'
            elif box_type == BOX_STOP:
                c = '.'
            else:
                c = '-'
            rogue_plane.create_terrain(
                s=s_nail,
                e=e_nail+i,
                c=c,
                cpair=cpair)
            rogue_plane.create_terrain(
                s=s_nail+height+1,
                e=e_nail+i,
                c=c,
                cpair=cpair)
    for i in range(height):
        if box_type == BOX_HASH:
            c = '#'
        elif box_type == BOX_STOP:
            c = '.'
        else:
            c = '|'
        rogue_plane.create_terrain(
            s=s_nail+i+1,
            e=e_nail,
            c=c,
            cpair=cpair)
        rogue_plane.create_terrain(
            s=s_nail+i+1,
            e=e_nail+width+1,
            c=c,
            cpair=cpair)


# --------------------------------------------------------
#   :alg
# --------------------------------------------------------
def prep_plane(rogue_plane):
    #
    # // terrain: walls
    make_box(
        rogue_plane=rogue_plane,
        se_nail=(-5, -8),
        width=30,
        height=14,
        box_type=BOX_STOP)
    make_box(
        rogue_plane=rogue_plane,
        se_nail=(6, 3),
        width=1,
        height=1)
    make_box(
        rogue_plane=rogue_plane,
        se_nail=(-2, -17),
        width=3,
        height=3,
        cpair=SOL_CPAIR_CYAN_T,
        box_type=BOX_EDGE)
    make_box(
        rogue_plane=rogue_plane,
        se_nail=(-2, 10),
        width=3,
        height=3,
        cpair=SOL_CPAIR_CYAN_T,
        box_type=BOX_VOID)
    make_box(
        rogue_plane=rogue_plane,
        se_nail=(4, 10),
        width=3,
        height=3,
        cpair=SOL_CPAIR_CYAN_T,
        box_type=BOX_STOP)
    make_box(
        rogue_plane=rogue_plane,
        se_nail=(-4, 28),
        width=3,
        height=3,
        box_type=BOX_HASH)
    make_box(
        rogue_plane=rogue_plane,
        se_nail=(4, 28),
        width=3,
        height=3,
        box_type=BOX_STOP)
    #
    # // terrain: boulder
    rogue_plane.create_terrain(
        s=-1,
        e=-3,
        c='o')
    #
    # // terrain: standing stones
    rogue_plane.create_terrain(
        s=-2,
        e=-2,
        c='i',
        cpair=SOL_CPAIR_WHITE_T)
    rogue_plane.create_terrain(
        s=-3,
        e=0,
        c='i',
        cpair=SOL_CPAIR_WHITE_T)
    rogue_plane.create_terrain(
        s=-2,
        e=2,
        c='i',
        cpair=SOL_CPAIR_WHITE_T)
    rogue_plane.create_terrain(
        s=0,
        e=-3,
        c='i',
        cpair=SOL_CPAIR_WHITE_T)
    rogue_plane.create_terrain(
        s=0,
        e=3,
        c='i',
        cpair=SOL_CPAIR_WHITE_T)
    rogue_plane.create_terrain(
        s=2,
        e=-2,
        c='i',
        cpair=SOL_CPAIR_WHITE_T)
    rogue_plane.create_terrain(
        s=3,
        e=0,
        c='i',
        cpair=SOL_CPAIR_WHITE_T)
    rogue_plane.create_terrain(
        s=2,
        e=2,
        c='i',
        cpair=SOL_CPAIR_WHITE_T)
    #
    # // scrap
    rogue_plane.create_meep(
        s=3,
        e=-4,
        c=':',
        cpair=SOL_CPAIR_YELLOW_T)
    #
    # // meeps
    rogue_plane.create_meep(
        s=3,
        e=3,
        c='"',
        cpair=SOL_CPAIR_GREEN_T)

def event_loop(console, keystream, grid_display):
    console.redraw(grid_display)
    while True:
        console.accept(
            key=keystream.next())
        console.redraw(grid_display)

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
        time_system = time_system_new()
        #
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
        rogue_console = rogue_console_new(
            rogue_game=rogue_game,
            width=C_GAME_WIDTH,
            height=C_GAME_HEIGHT,
            cursor=cursor)
        #
        experience_console = experience_console_new(
            title=TITLE,
            console=rogue_console)
        #
        term_shape = fn_device_start(
            game_width=C_GAME_WIDTH,
            game_height=C_GAME_HEIGHT)
        #
        # event loop
        event_loop(
            console=experience_console,
            keystream=term_shape.get_keystream(),
            grid_display=term_shape.get_grid_display())
    except SolentQuitException:
        pass
    except:
        traceback.print_exc()
    finally:
        fn_device_end()

if __name__ == '__main__':
    main()

