#!/usr/bin/python -B
#
# qd_listen
#
# // overview
# Quick-and-dirty udp-broadcast listener. This tool is used for testing
# some of the scenarios.
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

from solent.eng import create_engine
from solent.log import init_logging
from solent.log import log
from solent.log import nicehex

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

def operate_a_udp_broadcast_listener(engine, net_addr, net_port):
    #
    print('''test this with
        echo "Hello" | socat - UDP-DATAGRAM:%s:%s,broadcast
    '''%(net_addr, net_port))
    #
    # We'll gather data to here
    class Cog(object):
        def __init__(self):
            self.sid = engine.open_broadcast_listener(
                addr=net_addr,
                port=net_port,
                cb_sub_recv=self.engine_on_sub_recv)
            self.accumulate = []
        def engine_on_sub_recv(self, cs_sub_recv):
            engine = cs_sub_recv.engine
            sub_sid = cs_sub_recv.sub_sid
            data = cs_sub_recv.data
            #
            self.accumulate.append(data)
        def pull(self):
            s = ''.join([str(b) for b in self.accumulate])
            self.accumulate = []
            return s
    #
    # By this point we have a nice reactor-like thing all set
    # up and ready-to-go held within engine_api. All we need to
    # do is to run our while loop, with most of the work to
    # be done for select having been exported to that module.
    class Orb(object):
        def __init__(self):
            self.cog = Cog()
        def at_turn(self):
            activity = False
            data = self.cog.pull()
            if data:
                activity = True
                nicehex(data, 'Received from %s:%s'%(net_addr, net_port))
            return activity
    orb = Orb()
    engine.add_orb(orb)
    engine.event_loop()

def main():
    if '--help' in sys.argv:
        quickstart()
    if 3 != len(sys.argv):
        usage()
    #
    init_logging()
    engine = create_engine()
    try:
        net_addr = sys.argv[1]
        net_port = int(sys.argv[2])
        operate_a_udp_broadcast_listener(
            engine=engine,
            net_addr=net_addr,
            net_port=net_port)
    except:
        traceback.print_exc()
    finally:
        engine.close()

if __name__ == '__main__':
    main()

