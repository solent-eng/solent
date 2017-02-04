#!/usr/bin/python -B
#
# qd_poll
#
# // overview
# Simple UDP broadcaster.
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
from solent.log import init_logging
from solent.log import log
from solent.log import hexdump_bytes

import sys
import time
import traceback

I_NEARCAST_SCHEMA = '''
    i message h
        i field h

    message init
        field addr
        field port
'''

def usage():
    print('Usage:')
    print('  %s broadcast_addr port'%sys.argv[0])
    sys.exit(1)

class CogUdpSender:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.pub_sid = None
        self.t_last = None
    def at_turn(self, activity):
        if self.pub_sid == None:
            return
        now = time.time()
        if now - self.t_last > 2:
            log('send!')
            self.t_last = now
            self.engine.send(
                sid=self.pub_sid,
                bb=bytes('message at [%s]\n'%now, 'utf8'))
    def at_close(self):
        self.engine.close_broadcast_listener(
            sid=self.pub_sid)
        self.pub_sid = None
    def on_init(self, addr, port):
        self.engine.open_pub(
            addr=addr,
            port=port,
            cb_pub_start=self._engine_on_pub_start,
            cb_pub_stop=self._engine_on_pub_stop)
        self.t_last = 0
    def _engine_on_pub_start(self, cs_pub_start):
        engine = cs_pub_start.engine
        pub_sid = cs_pub_start.pub_sid
        addr = cs_pub_start.addr
        port = cs_pub_start.port
        #
        self.pub_sid = pub_sid
    def _engine_on_pub_stop(self, cs_pub_stop):
        engine = cs_pub_stop.engine
        pub_sid = cs_pub_stop.pub_sid
        message = cs_pub_stop.message
        #
        self.pub_sid = None

class CogBridge:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
    def nc_init(self, addr, port):
        self.nearcast.init(
            addr=addr,
            port=port)

def main():
    if 3 != len(sys.argv):
        usage()
    #
    init_logging()
    engine = engine_new(
        mtu=1492)
    try:
        net_addr = sys.argv[1]
        net_port = int(sys.argv[2])
        #
        orb = engine.init_orb(
            spin_h=__name__,
            i_nearcast=I_NEARCAST_SCHEMA)
        orb.init_cog(CogUdpSender)
        bridge = orb.init_cog(CogBridge)
        bridge.nc_init(
            addr=net_addr,
            port=net_port)
        #
        engine.event_loop()
    except KeyboardInterrupt:
        pass
    except:
        traceback.print_exc()
    finally:
        engine.close()

if __name__ == '__main__':
    main()


