#
# prop_gruel_client
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

from solent.log import log
from solent.util import ns

from collections import deque
from collections import OrderedDict as od

#
# xxx connect pattern
'''
engine.open_tcp_client(
    addr=addr,
    port=port,
    cb_tcp_connect=self._engine_on_tcp_connect,
    cb_tcp_confail=self._engine_on_tcp_confail,
    cb_tcp_recv=self._engine_on_tcp_recv)
'''

class PropGruelClient:
    def __init__(self, engine):
        self.engine = engine
        #
        # form: (addr, port) : deque containing data
        self.q_received = deque()
        self.client_sid = None
    def close(self):
        self.engine.close_tcp_server(self.server_sid)
    def at_turn(self, activity):
        pass
    #
    def _engine_on_tcp_connect(self, cs_tcp_connect):
        engine = cs_tcp_connect.engine
        client_sid = cs_tcp_connect.client_sid
        addr = cs_tcp_connect.addr
        port = cs_tcp_connect.port
        #
        log("connect/%s/%s/%s/%s"%(
            self.cog_h,
            client_sid,
            addr,
            port))
        engine.send(
            sid=client_sid,
            data='')
    def _engine_on_tcp_confail(self, cs_tcp_confail):
        engine = cs_tcp_confail.engine
        client_sid = cs_tcp_confail.client_sid
        message = cs_tcp_confail.message
        #
        log("confail/%s/%s/%s"%(self.cog_h, client_sid, message))
        while self.q_received:
            self.q_received.pop()
    def _engine_on_tcp_recv(self, cs_tcp_recv):
        engine = cs_tcp_recv.engine
        client_sid = cs_tcp_recv.client_sid
        data = cs_tcp_recv.data
        #
        self.q_received.append(data)
        engine.send(
            sid=client_sid,
            data='q_received %s\n'%len(data))

def prop_gruel_client_new(engine):
    ob = PropGruelClient(
        engine=engine)
    return ob

