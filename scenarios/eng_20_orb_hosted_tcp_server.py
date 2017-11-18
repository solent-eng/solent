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
# // Overview
# Here, we host a TCP server within a nearcast. A quirk of this server is
# that it closes whenever it /accepts/ a connection. Hence, you can only
# have one client connected at a time. This is done for simplicity.
# Technically it's not a blocking TCP connection, but it behaves in a
# similar way to one.

from solent import Engine
from solent import log
from solent import SolentQuitException

I_NEARCAST = '''
    i message h
        i field h

    message init
    message exit
'''

MTU = 1400

TCP_SERVER_ADDR = '0.0.0.0'
TCP_SERVER_PORT = 8000

class CogTcpServer:
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
    #
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
        log('cb_tcp_accept_recv [%s]'%(msg))
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

def init(engine):
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST)
    orb.init_cog(CogTcpServer)
    #
    bridge = orb.init_autobridge()
    bridge.nc_init()

def main():
    engine = Engine(
        mtu=MTU)
    try:
        init(
            engine=engine)
        engine.event_loop()
    except KeyboardInterrupt:
        pass
    except SolentQuitException:
        pass
    finally:
        engine.close()

if __name__ == '__main__':
    main()

