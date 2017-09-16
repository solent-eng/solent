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
from solent import log
from solent.util import RailLineFinder


# --------------------------------------------------------
#   model
# --------------------------------------------------------
I_NEARCAST = '''
    i message h
    i field h

    message init
        field net_addr
        field net_port
    message exit

    message received_from_network
        field msg
'''

class RailBroadcastListener:
    def __init__(self, engine, cb_found_line):
        self.engine = engine
        self.cb_found_line = cb_found_line
        #
        self.sub_sid = None
        self.rail_line_finder = RailLineFinder()
        self.rail_line_finder.zero(
            cb_found_line=cb_found_line)
    #
    def start(self, ip, port):
        self.engine.open_sub(
            addr=ip,
            port=port,
            cb_sub_start=self.cb_sub_start,
            cb_sub_stop=self.cb_sub_stop,
            cb_sub_recv=self.cb_sub_recv)
    def stop(self):
        self.engine.close_sub(
            sub_sid=self.sub_sid)
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
        log('sub stopped %s'%sub_sid)
        #
        self.sub_sid = None
        self.rail_line_finder.clear()
    def cb_sub_recv(self, cs_sub_recv):
        engine = cs_sub_recv.engine
        sub_sid = cs_sub_recv.sub_sid
        bb = cs_sub_recv.bb
        #
        log('sub recv (len %s)'%(len(bb)))
        #
        self.rail_line_finder.accept_bytes(
            bb=bb)

class CogBroadcastListener:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.rail_broadcast_listener = None
    #
    def on_init(self, net_addr, net_port):
        self.rail_broadcast_listener = RailBroadcastListener(
            engine=self.engine,
            cb_found_line=self.cb_found_line)
        self.rail_broadcast_listener.start(
            ip=net_addr,
            port=net_port)
    #
    def cb_found_line(self, cs_found_line):
        msg = cs_found_line.msg
        #
        self.nearcast.received_from_network(
            msg=msg)

class CogPrinter:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
    def on_received_from_network(self, msg):
        log('! received [%s] :)'%(msg))


# --------------------------------------------------------
#   launch
# --------------------------------------------------------
MTU = 1350

NET_ADDR = '127.255.255.255'
NET_PORT = 50000

def app():
    engine = Engine(
        mtu=MTU)
    #
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST)
    orb.init_cog(CogBroadcastListener)
    orb.init_cog(CogPrinter)
    #
    bridge = orb.init_autobridge()
    bridge.nc_init(
        net_addr=NET_ADDR,
        net_port=NET_PORT)
    #
    # You can use this to print more info about the event loop. This would be
    # useful if you had a flailing event loop and could not work out what was
    # causing the activity.
    engine.debug_eloop_on()
    engine.event_loop()

def main():
    print('''test this with
        echo "Hello" | socat - UDP-DATAGRAM:%s:%s,broadcast
    Or
        python3 -m solent.tools.qd_poll 127.255.255.255 50000
    '''%(NET_ADDR, NET_PORT))
    try:
        app()
    except KeyboardInterrupt:
        pass
    except SolentQuitException:
        pass

if __name__ == '__main__':
    main()

