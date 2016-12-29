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

from solent.eng import engine_new
from solent.eng import nearcast_schema_new
from solent.exceptions import SolentQuitException
from solent.log import init_logging
from solent.log import log
from solent.term import spin_term_new
from solent.util import uniq
from solent.winconsole import window_console_new

from collections import deque
import os
import sys
import time
import traceback

MTU = 1500

I_NEARCAST_SCHEMA = '''
    i message h
        i field h

    message keystroke
        field keycode
'''

class CogInterpreter(object):
    def __init__(self, cog_h, engine, orb):
        self.cog_h = cog_h
        self.engine = engine
        self.orb = orb
    def on_keystroke(self, keycode):
        log('key received %s'%keycode)
        if keycode == ord('Q'):
            raise SolentQuitException()

class CogConsole(object):
    def __init__(self, cog_h, engine, orb):
        self.cog_h = cog_h
        self.engine = engine
        self.orb = orb
        #
        width = 10
        height = 20
        #
        self.cgrid = cgrid_new(
            width=width,
            height=height)
        self.keys = deque()
        self.console = window_console_new(
            width=width,
            height=height)
    def close(self):
        self.console.close()
    def at_turn(self, activity):
        self.console.screen_update(
            cgrid=self.cgrid)
        key = self.console.async_getc()
        if key:
            activity.mark(
                l=self,
                s='received keystroke')
            self.orb.nearcast(
                cog=self,
                message_h='keystroke',
                keycode=ord(key))
    def on_keystroke(self, keycode):
        self.cgrid.put(
            drop=0,
            rest=0,
            s='%4s'%(keycode),
            cpair=e_colpair.green_t)
        log('key received %s'%keycode)
        if keycode == ESC_KEY_ORD:
            raise SolentQuitException()

class CogTerm(object):
    def __init__(self, cog_h, engine, orb):
        self.cog_h = cog_h
        self.engine = engine
        self.orb = orb
        #
        self.spin_term = spin_term_new(
            cb_keycode=self.term_on_keycode,
            cb_select=self.term_on_select)
        self.spin_term.open_console(
            width=20,
            height=10)
    def close(self):
        self.spin_term.close()
    def at_turn(self, activity):
        self.spin_term.at_turn(
            activity=activity)
    def term_on_keycode(self, keycode):
        self.orb.nearcast(
            cog=self,
            message_h='keystroke',
            keycode=keycode)
    def term_on_select(self, drop, rest):
        # user makes a selection
        log('xxx term_on_select drop %s rest %s'%(drop, rest))

def main():
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
        orb.init_cog(CogInterpreter)
        #orb.init_cog(CogConsole)
        orb.init_cog(CogTerm)
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

