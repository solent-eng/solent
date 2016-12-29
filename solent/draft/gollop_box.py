#!/usr/bin/env python3
#
# gollop box
#
# // overview
# I'm adding a mechanism to the console where you can select things in the
# current grid using a gollop-like interface. This is the vehicle for playing
# with that idea.
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

from solent.draft.turnlib.algobunny_mind import algobunny_mind_new
from solent.draft.turnlib.menu import menu_new
from solent.draft.turnlib.player_mind import player_mind_new
from solent.draft.turnlib.rogue_interaction import rogue_interaction_new
from solent.draft.turnlib.rogue_plane import rogue_plane_new
from solent.draft.turnlib.initiative import initiative_new
from solent.eng import engine_new
from solent.exceptions import SolentQuitException
from solent.log import init_logging
from solent.log import log
from solent.console import e_colpair
from solent.console import e_boxtype
from solent.console import cgrid_new
from solent.console import cursor_new
from solent.util import uniq
from solent.winconsole import window_console_end
from solent.winconsole import window_console_start

from collections import deque
import os
import sys
import time
import traceback

ESC_KEY_ORD = 27

C_GAME_WIDTH = 78
C_GAME_HEIGHT = 25

MTU = 1500

TITLE = sys.argv[0].split(os.sep)[-1]

class CogPanel(object):
    def __init__(self, engine, console):
        self.engine = engine
        self.console = console
        #
        self.keys = deque()
    def event_loop(self):
        self._render()
        while True:
            sys.exit(1) # xxx


# --------------------------------------------------------
#   :alg
# --------------------------------------------------------
I_NEARCAST_SCHEMA = '''
    i message h
    i field h
'''

def engine_layer():
    engine = engine_new(
        mtu=1500)
    try:
        nearcast_schema = nearcast_schema_new(
            i_nearcast=I_NEARCAST_SCHEMA)
        orb = engine.init_orb(
            orb_h=__name__,
            nearcast_schema=nearcast_schema)
        orb.add_log_snoop()
        #
        orb.init_cog(CogPanel)
        #
        uplink = orb.init_cog(CogUplink)
        uplink.nc_permit_client_ip(
            ip='127.0.0.1')
        #
        engine.event_loop()
    except KeyboardInterrupt:
        pass
    except:
        traceback.print_exc()
    finally:
        engine.close()

def console_layer():
    try:
        engine = engine_new(
            mtu=MTU)
        console = window_console_start(
            width=C_GAME_WIDTH,
            height=C_GAME_HEIGHT)
        panel = Panel(
            console=console)
        #
        # event loop
        panel.event_loop()
    except SolentQuitException:
        pass
    except:
        traceback.print_exc()
    finally:
        window_console_end()

def main():
    init_logging()
    console_layer()

if __name__ == '__main__':
    main()

