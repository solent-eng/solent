#!/usr/bin/python -B
#
# qd_listen
#
# // overview
# Quick-and-dirty udp-broadcast listener. This tool is used for testing
# some of the scenarios. This tool predates nearcasting, and is not
# currently a good example of the style.
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
import traceback

QUICKSTART = '''
    quickstart
    ========================================= 
    Open two terminals, term_a and term_b

    In term_a:
        # this will do a udp subscribe, and output events as they come
        python qd_listener.py 127.255.255.255 2221 

    In term_b:
        # this will broadcast a message on udp
        echo "Hello" | socat - UDP-DATAGRAM:127.255.255.255:2221,broadcast 
    ========================================= 
'''

def quickstart():
    print(QUICKSTART)
    sys.exit(0)

def usage():
    print('Usage:')
    print('  %s broadcast_addr port'%sys.argv[0])
    sys.exit(1)

class SpinUdpListener:
    def __init__(self, engine, cb_data):
        self.engine = engine
        self.cb_data = cb_data
        #
        self.sub_sid = None
        self.accumulate = []
    def start(self, ip, port):
        self.sub_sid = self.engine.open_broadcast_listener(
            addr=ip,
            port=port,
            cb_sub_recv=self.engine_on_sub_recv)
    def stop(self):
        self.close_broadcast_listener(
            sid=self.sub_sid)
    def engine_on_sub_recv(self, cs_sub_recv):
        engine = cs_sub_recv.engine
        sub_sid = cs_sub_recv.sub_sid
        data = cs_sub_recv.data
        #
        self.cb_data(
            data=data)

def operate_a_udp_broadcast_listener(engine, net_addr, net_port):
    #
    # We'll gather data to here
    class Cog(object):
        def __init__(self, cog_h, orb, engine):
            self.cog_h = cog_h
            self.orb = orb
            self.engine = engine
            #
            self.spin_udp_listener = SpinUdpListener(
                engine=engine,
                cb_data=self.spin_on_data)
            self.spin_udp_listener.start(
                ip=net_addr,
                port=net_port)
        def spin_on_data(self, data):
            hexdump_bytes(
                arr=data,
                title='Received')
    orb = engine.init_orb(
        orb_h=__name__,
        nearcast_schema=nearcast_schema_new(''))
    orb.init_cog(Cog)
    engine.event_loop()

def main():
    if '--help' in sys.argv:
        quickstart()
    if 3 != len(sys.argv):
        usage()
    #
    init_logging()
    engine = engine_new(
        mtu=1492)
    try:
        net_addr = sys.argv[1]
        net_port = int(sys.argv[2])
        operate_a_udp_broadcast_listener(
            engine=engine,
            net_addr=net_addr,
            net_port=net_port)
    except KeyboardInterrupt:
        pass
    except:
        traceback.print_exc()
    finally:
        engine.close()

if __name__ == '__main__':
    main()

