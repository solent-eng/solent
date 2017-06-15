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
# Here, we host a TCP server for a line console. A single client is able to
# connect. At this point, the server takes down its listen interface. This is
# not a blocking server, but shows the same behaviour to clients.
#
# There is an advance on the previous module in this series. Consider what
# would happen if the user submitted a long line, where the length exceeded
# the size of a single payload. Here, we filter all input through
# rail_line_finder. This calls back at the termination of a line, rather than
# making unreliable inferences about messages within payloads.
#
# This module serves an illustrative purpose. But if ever you need a netcat
# server such as this, please example solent.lc.spin_line_console. You may
# find it does what you need.

from solent import Engine
from solent import SolentQuitException
from solent.log import log
from solent.util import RailLineFinder

I_NEARCAST = '''
    i message h
        i field h

    message init
    message exit

    message user_line
        field msg
'''

MTU = 1400

TCP_SERVER_ADDR = '0.0.0.0'
TCP_SERVER_PORT = 8000

class CogAppConsole:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.b_active = False
        self.tcp_server_addr = None
        self.tcp_server_port = None
        self.server_sid = None
        self.accept_sid = None
        #
        self.rail_line_finder = RailLineFinder()
        self.rail_line_finder.zero(
            cb_found_line=self.cb_found_line)
    def orb_close(self):
        if self.server_sid:
            self._stop_server()
        if self.accept_sid:
            self.engine.close_tcp_server(
                server_sid=self.server_sid)
    #
    def on_init(self):
        self.tcp_server_addr = TCP_SERVER_ADDR
        self.tcp_server_port = TCP_SERVER_PORT
        #
        self.b_active = True
        self._start_server()
    def on_exit(self):
        self.b_active = False
        self._stop_server()
    #
    def cb_found_line(self, cs_found_line):
        msg = cs_found_line.msg
        #
        self.nearcast.user_line(
            msg=msg)
    def cb_tcp_server_start(self, cs_tcp_server_start):
        engine = cs_tcp_server_start.engine
        server_sid = cs_tcp_server_start.server_sid
        addr = cs_tcp_server_start.addr
        port = cs_tcp_server_start.port
        #
        self.server_sid = server_sid
        log('cb_tcp_server_start, sid %s, at %s:%s'%(server_sid, addr, port))
    def cb_tcp_server_stop(self, cs_tcp_server_stop):
        engine = cs_tcp_server_stop.engine
        server_sid = cs_tcp_server_stop.server_sid
        msg = cs_tcp_server_stop.message
        #
        self.server_sid = None
        log('cb_tcp_server_stop, sid %s, %s'%(server_sid, msg))
    def cb_tcp_accept_connect(self, cs_tcp_accept_connect):
        engine = cs_tcp_accept_connect.engine
        server_sid = cs_tcp_accept_connect.server_sid
        accept_sid = cs_tcp_accept_connect.accept_sid
        accept_addr = cs_tcp_accept_connect.accept_addr
        accept_port = cs_tcp_accept_connect.accept_port
        #
        log('cb_tcp_accept_connect from %s:%s'%(
            accept_addr, accept_port))
        self.engine.close_tcp_server(
            server_sid=self.server_sid)
        self.accept_sid = accept_sid
        self.rail_line_finder.clear()
    def cb_tcp_accept_condrop(self, cs_tcp_accept_condrop):
        engine = cs_tcp_accept_condrop.engine
        server_sid = cs_tcp_accept_condrop.server_sid
        accept_sid = cs_tcp_accept_condrop.accept_sid
        #
        log('cb_tcp_accept_condrop from %s'%(
            accept_sid))
        self.accept_sid = None
        if self.b_active:
            self._start_server()
    def cb_tcp_accept_recv(self, cs_tcp_accept_recv):
        engine = cs_tcp_accept_recv.engine
        accept_sid = cs_tcp_accept_recv.accept_sid
        bb = cs_tcp_accept_recv.bb
        #
        msg = bb.decode('utf8')
        self.rail_line_finder.accept_string(
            s=msg)
    #
    def _start_server(self):
        self.engine.open_tcp_server(
            addr=self.tcp_server_addr,
            port=self.tcp_server_port,
            cb_tcp_server_start=self.cb_tcp_server_start,
            cb_tcp_server_stop=self.cb_tcp_server_stop,
            cb_tcp_accept_connect=self.cb_tcp_accept_connect,
            cb_tcp_accept_condrop=self.cb_tcp_accept_condrop,
            cb_tcp_accept_recv=self.cb_tcp_accept_recv)
    def _stop_server(self):
        self.engine.close_tcp_server(
            server_sid=self.server_sid)

class CogPrinter:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
    def on_user_line(self, msg):
        log("Received line [%s]"%msg)

def run_scenario(engine):
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST)
    orb.init_cog(CogAppConsole)
    orb.init_cog(CogPrinter)
    #
    bridge = orb.init_autobridge()
    bridge.nc_init()
    #
    engine.event_loop()

def main():
    engine = Engine(
        mtu=MTU)
    try:
        run_scenario(
            engine=engine)
    except KeyboardInterrupt:
        pass
    except SolentQuitException:
        pass
    finally:
        engine.close()

if __name__ == '__main__':
    main()

