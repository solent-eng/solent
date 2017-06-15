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
from solent import SolentQuitException
from solent.log import log

import cProfile

MTU = 1300

I_NEARCAST = '''
    i message h
    i field h

    message init
    message exit

    message tick
        field n
'''

LIMIT = 100000

class CsCounterTick:
    def __init__(self):
        pass

class CsCounterTick:
    def __init__(self):
        pass

class CsCounterFini:
    def __init__(self):
        pass

class RailCounter:
    def __init__(self, limit, cb_counter_tick, cb_counter_fini):
        self.limit = limit
        self.cb_counter_tick = cb_counter_tick
        self.cb_counter_fini = cb_counter_fini
        #
        self.cs_counter_tick = CsCounterTick()
        self.cs_counter_fini = CsCounterFini()
        #
        self.n = 0
    def next(self):
        self.n += 1
        if self.n == self.limit:
            self.n = 0
            self._call_counter_fini()
    def _call_counter_tick(self):
        self.cs_counter_tick.n = self.n
        self.cb_counter_tick(
            cs_counter_tick=self.cs_counter_tick)
    def _call_counter_fini(self):
        self.cb_counter_fini(
            cs_counter_fini=self.cs_counter_fini)

class CogCounter:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.rail_counter = RailCounter(
            limit=LIMIT,
            cb_counter_tick=self.cb_counter_tick,
            cb_counter_fini=self.cb_counter_fini)
    def orb_turn(self, activity):
        activity.mark(
            l=self,
            s='counter')
        self.rail_counter.next()
    #
    #
    def cb_counter_tick(self, cs_counter_tick):
        n = cs_counter_tick.n
        #
        self.nearcast.tick(
            n=n)
    def cb_counter_fini(self, cs_counter_fini):
        self.nearcast.exit()

class CogWatcher:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
    def on_init(self):
        log('init')
    def on_exit(self):
        log('exit')
        raise SolentQuitException()
    def on_tick(self, n):
        if 0 == n % (LIMIT / 10):
            log('tick %s'%n)

def app():
    engine = Engine(
        mtu=MTU)
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST)
    orb.init_cog(CogCounter)
    orb.init_cog(CogWatcher)
    #
    bridge = orb.init_autobridge()
    bridge.nc_init()
    #
    engine.event_loop()

def main():
    pr = cProfile.Profile()
    pr.enable()
    #
    try:
        app()
    except KeyboardInterrupt:
        pass
    except SolentQuitException:
        pass
    #
    pr.disable()
    pr.print_stats(
        sort='time')

if __name__ == '__main__':
    main()

