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
#
# // overview
# Grabs what comes in on a UDP port, and sends it to stdout

from solent import Engine
from solent import log
from solent import SolentQuitException

import os
import sys
import time

MTU = 1492

I_NEARCAST = '''
    i message h
    i field h

    message prime
        field addr
        field port
    message init
'''

class TrackPrime:
    def __init__(self, orb):
        self.orb = orb
    def on_prime(self, addr, port):
        self.addr = addr
        self.port = port

class Cog:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.track_prime = orb.track(TrackPrime)
        #
        self.sub_sid = None
    def on_init(self):
        self.sub_sid = self.engine.open_sub(
            addr=self.track_prime.addr,
            port=self.track_prime.port,
            cb_sub_start=self.cb_sub_start,
            cb_sub_stop=self.cb_sub_stop,
            cb_sub_recv=self.cb_sub_recv)
    def cb_sub_start(self, cs_sub_start):
        pass
    def cb_sub_stop(self, cs_sub_stop):
        pass
    def cb_sub_recv(self, cs_sub_recv):
        bb = cs_sub_recv.bb
        #
        s = bb.decode('utf8')
        log(s)

def init_nearcast(engine, addr, port):
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST)
    orb.init_cog(Cog)
    bridge = orb.init_autobridge()
    bridge.nearcast.prime(
        addr=addr,
        port=port)
    bridge.nearcast.init()
    return bridge

def usage(exit_code=1):
    print('usage')
    print('  %s addr port'%(sys.argv[0]))
    sys.exit(exit_code)

def main():
    if '--help' in sys.argv:
        usage()
    if 3 != len(sys.argv):
        usage()
    (_, addr, port) = sys.argv
    port = int(port)
    #
    engine = Engine(
        mtu=MTU)
    try:
        init_nearcast(
            engine=engine,
            addr=addr,
            port=port)
        engine.event_loop()
    except KeyboardInterrupt:
        pass
    except SolentQuitException:
        pass
    finally:
        engine.close()

if __name__ == '__main__':
    main()

