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
# Quick-and-dirty udp-broadcast listener. This tool is used for testing
# scenarios.

from solent import Engine
from solent.log import log
from solent.log import hexdump_bytes

import sys
import traceback

I_NEARCAST = '''
    i message h
    i field h

    message init
        field net_addr
        field net_port
'''

class CsUdpBb:
    def __init__(self):
        self.bb = None

class RailUdpListener:
    def __init__(self, engine, cb_udp_bb):
        self.engine = engine
        self.cb_udp_bb = cb_udp_bb
        #
        self.cs_udp_bb = CsUdpBb()
        #
        self.sub_sid = None
        self.accumulate = []
    #
    def start(self, ip, port):
        self.sub_sid = self.engine.open_sub(
            addr=ip,
            port=port,
            cb_sub_start=self.cb_sub_start,
            cb_sub_stop=self.cb_sub_stop,
            cb_sub_recv=self.cb_sub_recv)
    def stop(self):
        self.close_broadcast_listener(
            sid=self.sub_sid)
    #
    def cb_sub_start(self, cs_sub_start):
        engine = cs_sub_start.engine
        sub_sid = cs_sub_start.sub_sid
        addr = cs_sub_start.addr
        port = cs_sub_start.port
        #
        log('sub %s started %s:%s'%(sub_sid, addr, port))
        #
        self.sub_sid = sub_sid
    def cb_sub_stop(self, cs_sub_stop):
        engine = cs_sub_stop.engine
        sub_sid = cs_sub_stop.sub_sid
        message = cs_sub_stop.message
        #
        log('sub stopped %s'%(sub_sid))
        #
        self.sub_sid = None
    def cb_sub_recv(self, cs_sub_recv):
        engine = cs_sub_recv.engine
        sub_sid = cs_sub_recv.sub_sid
        bb = cs_sub_recv.bb
        #
        self.cs_udp_bb.bb = bb
        self.cb_udp_bb(
            cs_udp_bb=self.cs_udp_bb)

class CogUdpListener(object):
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.rail_udp_listener = RailUdpListener(
            engine=engine,
            cb_udp_bb=self.cb_udp_bb)
    #
    def on_init(self, net_addr, net_port):
        self.rail_udp_listener.start(
            ip=net_addr,
            port=net_port)
    #
    def cb_udp_bb(self, cs_udp_bb):
        bb = cs_udp_bb.bb
        #
        hexdump_bytes(
            arr=bb,
            title='Received')

def app(net_addr, net_port):
    engine = Engine(
        mtu=1492)
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST)
    orb.init_cog(CogUdpListener)
    #
    bridge = orb.init_autobridge()
    bridge.nc_init(
        net_addr=net_addr,
        net_port=net_port)
    #
    engine.event_loop()

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

def main():
    if '--help' in sys.argv:
        quickstart()
    if 3 != len(sys.argv):
        usage()
    net_addr = sys.argv[1]
    net_port = int(sys.argv[2])
    #
    try:
        app(
            net_addr=net_addr,
            net_port=net_port)
    except KeyboardInterrupt:
        pass
    except:
        traceback.print_exc()

if __name__ == '__main__':
    main()

