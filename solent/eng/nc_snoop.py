#
# nc snoop
#
# // overview
# Hosts a network service that allows a developer to see each of the messages
# on a nearcast as they happen.
#
# The nc is meant to imply netcat rather than nearcast. There's also a valid
# nearcast snoop called log_snoop.
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

from collections import deque

class NetSnoop:
    '''
    This gives you a network service that allows you to use netcat or similar
    to see all the messages that are passing through the nearcast. Useful
    for debugging. The snoop behaves a lot like a cog, but has different
    construction arrangements.

    Allows a user to snoop on the messages on a nearcast. This is typically
    contained within a NearcastOrb.
    
    This class is similar to a cog. However, the mechanism by which it
    receives nearcast messages is different to cogs. Cogs implement an
    on_message_h method. Whereas this gets everything in on_nearcast_message.
    And that requires special logic in NearcastOrb.

    This behaves like a blocking server (only one client at a time).
    '''
    def __init__(self, engine, nearcast_schema, addr, port):
        self.engine = engine
        self.nearcast_schema = nearcast_schema
        self.addr = addr
        self.port = port
        #
        self.server_sid = None
        self.client_sid = None
        self.q_outbound = None
        #
        self._open_server()
    def close(self):
        self._close_server()
    def at_turn(self, activity):
        if self.q_outbound:
            activity.mark(
                l=self,
                s='processing q_outbound')
            while self.q_outbound:
                data = self.q_outbound.popleft()
                self.engine.send(
                    sid=self.client_sid,
                    data='%s\n'%(data))
    #
    def _open_server(self):
        self.server_sid = self.engine.open_tcp_server(
            addr=self.addr,
            port=self.port,
            cb_tcp_connect=self.engine_on_tcp_connect,
            cb_tcp_condrop=self.engine_on_tcp_condrop,
            cb_tcp_recv=self.engine_on_tcp_recv)
    def _close_server(self):
        self.engine.close_tcp_server(
            sid=self.server_sid)
        self.server_sid = None
    #
    def engine_on_tcp_connect(self, cs_tcp_connect):
        engine = cs_tcp_connect.engine
        client_sid = cs_tcp_connect.client_sid
        addr = cs_tcp_connect.addr
        port = cs_tcp_connect.port
        #
        self._close_server()
        self.q_outbound = deque()
        self.client_sid = client_sid
        log("connect/[snoop]/%s/%s/%s"%(
            client_sid,
            addr,
            port))
    def engine_on_tcp_condrop(self, cs_tcp_condrop):
        engine = cs_tcp_condrop.engine
        client_sid = cs_tcp_condrop.client_sid
        message = cs_tcp_condrop.message
        #
        log("condrop/[snoop]/%s/%s"%(client_sid, message))
        self.client_sid = None
        self.q_outbound = None
        self._open_server()
    def engine_on_tcp_recv(self, cs_tcp_recv):
        engine = cs_tcp_recv.engine
        client_sid = cs_tcp_recv.client_sid
        data = cs_tcp_recv.data
        #
        pass
    #
    def on_nearcast_message(self, cog_h, message_h, d_fields):
        if not self.client_sid:
            return
        def format_message():
            sb = []
            sb.append('%s>%s'%(cog_h, message_h))
            for key in self.nearcast_schema[message_h]:
                sb.append('%s:%s'%(key, d_fields[key]))
            return '/'.join(sb)
        nice = format_message()
        self.q_outbound.append(nice)

def nc_snoop_new(engine, nearcast_schema, addr, port):
    ob = NetSnoop(
        engine=engine,
        nearcast_schema=nearcast_schema,
        addr=addr,
        port=port)
    return ob

