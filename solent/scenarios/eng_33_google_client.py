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

from solent import SolentQuitException
from solent.eng import engine_new

MTU = 1400

I_NEARCAST = '''
    i message h
    i field h

    message init
    message exit
        field yn_success

    message get
        field addr
        field port
        field path
    message result
        field content
'''

class CogCoordinator:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
    def on_init(self):
        self.nearcast.get(
            addr='google.com',
            port=80,
            path='/index.html')
    def on_exit(self, yn_success):
        if yn_success == 'y':
            raise SolentQuitException()
        else:
            raise Exception("Failed lookup")
    def on_result(self, content):
        print(content)
        self.nearcast.exit(
            yn_success='y')

class CogTcpClient:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.http_get = None
        self.sb_recv = []
    def on_get(self, addr, port, path):
        self.http_get = 'GET %s HTTP/1.1\r\nhost: www.google.com\r\n\r\n'%path
        self.engine.open_tcp_client(
            addr=addr,
            port=port,
            cb_tcp_client_connect=self.cb_tcp_client_connect,
            cb_tcp_client_condrop=self.cb_tcp_client_condrop,
            cb_tcp_client_recv=self.cb_tcp_client_recv)
    def cb_tcp_client_connect(self, cs_tcp_client_connect):
        engine = cs_tcp_client_connect.engine
        client_sid = cs_tcp_client_connect.client_sid
        addr = cs_tcp_client_connect.addr
        port = cs_tcp_client_connect.port
        #
        self.engine.send(
            sid=client_sid,
            bb=bytes(self.http_get, 'utf8'))
    def cb_tcp_client_condrop(self, cs_tcp_client_condrop):
        engine = cs_tcp_client_condrop.engine
        client_sid = cs_tcp_client_condrop.client_sid
        message = cs_tcp_client_condrop.message
        #
        if len(self.sb_recv) == 0:
            self.nearcast.exit(
                yn_success='n')
    def cb_tcp_client_recv(self, cs_tcp_client_recv):
        engine = cs_tcp_client_recv.engine
        client_sid = cs_tcp_client_recv.client_sid
        bb = cs_tcp_client_recv.bb
        #
        msg = bb.decode('utf8')
        self.nearcast.result(
            content=msg)

def app():
    engine = engine_new(MTU)
    orb = engine.init_orb(I_NEARCAST)
    orb.init_cog(CogCoordinator)
    orb.init_cog(CogTcpClient)
    bridge = orb.init_autobridge()
    bridge.nc_init()
    engine.event_loop()

def main():
    try:
        app()
    except SolentQuitException:
        pass

if __name__ == '__main__':
    main()

