#!/usr/bin/python
#
# Intends to demonstrate basic use of the experience class
#

from .turnlib.control_menu import control_menu_new
from .turnlib.player_mind import player_mind_new
from .turnlib.rogue_interaction import rogue_interaction_new
from .turnlib.rogue_plane import rogue_plane_new
from .turnlib.time_system import time_system_new

from solent.client.constants import *
from solent.client.term.cgrid import cgrid_new
from solent.client.term.cursor import cursor_new
from solent.client.term.curses_console import curses_console_start, curses_console_end
from solent.client.term.window_console import window_console_start, window_console_end
from solent.exceptions import SolentQuitException
from solent.util import uniq

import os
import sys
import traceback

C_GAME_WIDTH = 78
C_GAME_HEIGHT = 25

TITLE = '[demo_experience]'


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
#   :game
# --------------------------------------------------------
def create_origin_plane():
    rogue_plane = rogue_plane_new()
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
    return rogue_plane


# --------------------------------------------------------
#   :event_loop
# --------------------------------------------------------
ESC_KEY = 27

def event_loop(console, player_mind, time_system):
    control_menu = control_menu_new(
        title=TITLE,
        console=console)
    control_menu.render()
    while True:
        #
        # Input
        key = console.getc()
        if key in (None, ''):
            continue
        #
        # Menu
        if control_menu.active() and ord(key) == ESC_KEY:
            control_menu.set_active(False)
            key = None
        elif not control_menu.active() and ord(key) == ESC_KEY:
            control_menu.set_active(True)
            key = None
        elif control_menu.active():
            control_menu.accept(
                key=key)
            key = None
        #
        # Game input
        if not control_menu.active():
            if key != None:
                player_mind.add_key(key)
            time_system.dispatch_next_tick()
        #
        # Menu display
        if control_menu.active():
            control_menu.render()


# --------------------------------------------------------
#   :alg
# --------------------------------------------------------
def main():
    if '--tty' in sys.argv:
        fn_device_start = curses_console_start
        fn_device_end = curses_console_end
    elif '--win' in sys.argv:
        fn_device_start = window_console_start
        fn_device_end = window_console_end
    else:
        print('ERROR: specify --tty or --win')
        sys.exit(1)
    try:
        console = fn_device_start(
            width=C_GAME_WIDTH,
            height=C_GAME_HEIGHT)
        #
        time_system = time_system_new()
        #
        rogue_plane = create_origin_plane()
        player_meep = rogue_plane.create_meep(
            s=0,
            e=0,
            c='@',
            cpair=SOL_CPAIR_RED_T)
        #
        rogue_interaction = rogue_interaction_new(
            console=console,
            cursor=cursor_new(
                fn_s=lambda: player_meep.coords.s,
                fn_e=lambda: player_meep.coords.e,
                fn_c=lambda: player_meep.c,
                fn_cpair=lambda: player_meep.cpair))
        #
        player_mind = player_mind_new(
            console=console,
            rogue_interaction=rogue_interaction)
        player_meep.mind = player_mind
        time_system.add_meep(
            meep=player_meep)
        #
        # event loop
        event_loop(
            console=console,
            player_mind=player_mind,
            time_system=time_system)
    except SolentQuitException:
        pass
    except:
        traceback.print_exc()
    finally:
        fn_device_end()

if __name__ == '__main__':
    main()

