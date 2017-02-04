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
    def __init__(self, spin_h, engine, cb_bb):
        self.spin_h = spin_h
        self.engine = engine
        self.cb_bb = cb_bb
        #
        self.b_active = False
        self.sub_sid = None
        self.accumulate = []
    def at_turn(self, activity):
        pass
    def at_close(self):
        pass
    #
    def start(self, ip, port):
        self.b_active = True
        self.sub_sid = self.engine.open_sub(
            addr=ip,
            port=port,
            cb_sub_start=self._engine_on_sub_start,
            cb_sub_stop=self._engine_on_sub_stop,
            cb_sub_recv=self._engine_on_sub_recv)
    def stop(self):
        self.b_active = False
        self.close_broadcast_listener(
            sid=self.sub_sid)
    #
    def _engine_on_sub_start(self, cs_sub_start):
        engine = cs_sub_start.engine
        sub_sid = cs_sub_start.sub_sid
        addr = cs_sub_start.addr
        port = cs_sub_start.port
        #
        log('sub %s started %s:%s'%(sub_sid, addr, port))
        #
        self.sub_sid = sub_sid
    def _engine_on_sub_stop(self, cs_sub_stop):
        engine = cs_sub_stop.engine
        sub_sid = cs_sub_stop.sub_sid
        message = cs_sub_stop.message
        #
        log('sub stopped %s'%(sub_sid))
        #
        self.sub_sid = None
    def _engine_on_sub_recv(self, cs_sub_recv):
        engine = cs_sub_recv.engine
        sub_sid = cs_sub_recv.sub_sid
        bb = cs_sub_recv.bb
        #
        self.cb_bb(
            bb=bb)

def operate_a_udp_broadcast_listener(engine, net_addr, net_port):
    #
    # We'll gather data to here
    class CogUdpListener(object):
        def __init__(self, cog_h, orb, engine):
            self.cog_h = cog_h
            self.orb = orb
            self.engine = engine
            #
            self.spin_udp_listener = engine.init_spin(
                construct=SpinUdpListener,
                cb_bb=self.spin_on_bb)
            self.spin_udp_listener.start(
                ip=net_addr,
                port=net_port)
        def spin_on_bb(self, bb):
            hexdump_bytes(
                arr=bb,
                title='Received')
    orb = engine.init_orb(
        spin_h=__name__,
        i_nearcast='')
    orb.init_cog(CogUdpListener)
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

