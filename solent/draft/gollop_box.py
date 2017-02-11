#!/usr/bin/env python3
#
# gollop box
#
# // overview
# Sandbox used for developing gollop-style selection within spin_term.
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
from solent import uniq
from solent.eng import engine_new
from solent.exceptions import SolentQuitException
from solent.log import init_logging
from solent.log import log
from solent.term import spin_term_new

from collections import deque
import os
import sys
import time
import traceback

MTU = 1500

CONSOLE_WIDTH = 60
CONSOLE_HEIGHT = 20

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

class CogTerm(object):
    def __init__(self, cog_h, engine, orb):
        self.cog_h = cog_h
        self.engine = engine
        self.orb = orb
        #
        self.counter = 0
        self.spin_term = self.engine.init_spin(
            construct=spin_term_new,
			console_type='pygame',
            cb_keycode=self.term_on_keycode,
            cb_select=self.term_on_select)
        self.spin_term.open_console(
            width=CONSOLE_WIDTH,
            height=CONSOLE_HEIGHT)
        self.spin_term.write(
            drop=0,
            rest=0,
            s='Escape toggles selection mode.',
            cpair=solent_cpair('green'))
        self.spin_term.write(
            drop=1,
            rest=0,
            s='Press Q to quit (when selection mode is off).',
            cpair=solent_cpair('green'))
    def at_turn(self, activity):
        self.spin_term.write(
            drop=6,
            rest=2,
            s=self.counter,
            cpair=solent_cpair('blue'))
        self.counter += 1
        #
        self.spin_term.at_turn(
            activity=activity)
    def term_on_keycode(self, keycode):
        self.nearcast.keystroke(
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
        orb = engine.init_orb(
            spin_h=__name__,
            i_nearcast=I_NEARCAST_SCHEMA)
        orb.init_cog(CogInterpreter)
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

