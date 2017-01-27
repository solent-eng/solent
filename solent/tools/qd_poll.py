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
from solent.eng import nearcast_schema_new
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
        self.sid_broadcast_sender = None
        self.t_last = None
    def at_close(self):
        self.engine.close_broadcast_listener(
            sid=self.sid_broadcast_sender)
        self.sid_broadcast_sender = None
    def on_init(self, addr, port):
        self.sid_broadcast_sender = self.engine.open_broadcast_sender(
            addr=addr,
            port=port)
        self.t_last = 0
    def at_turn(self, activity):
        if self.sid_broadcast_sender == None:
            return
        now = time.time()
        if now - self.t_last > 2:
            self.t_last = now
            self.engine.send(
                sid=self.sid_broadcast_sender,
                payload=bytes('message at [%s]'%now, 'utf8'))

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
        nearcast_schema = nearcast_schema_new(
            i_nearcast=I_NEARCAST_SCHEMA)
        orb = engine.init_orb(
            orb_h=__name__,
            nearcast_schema=nearcast_schema)
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


