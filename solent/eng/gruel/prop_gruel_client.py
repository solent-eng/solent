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
from solent.util import uniq
from solent.eng import gruel_press_new

from collections import deque
from collections import OrderedDict as od
from enum import Enum

class ClientStatus(Enum):
    dormant = uniq()
    attempting_tcp_connection = uniq()
    ready_to_attempt_login = uniq()
    login_message_in_flight = uniq()

class PropGruelClient:
    def __init__(self, engine, gruel_press, gruel_puff):
        self.engine = engine
        self.gruel_press = gruel_press
        self.gruel_puff = gruel_puff
        #
        self.status = ClientStatus.dormant
        self.login_credentials = ns()
        #
        # form: (addr, port) : deque containing data
        self.cb_connect = None
        self.cb_condrop = None
        self.q_received = deque()
        self.client_sid = None
    def close(self):
        self.engine.close_tcp_server(self.server_sid)
    def at_turn(self, activity):
        if self.status == ClientStatus.ready_to_attempt_login:
            self._attempt_login()
            activity.mark(
                l=self.__class__.__name__,
                s='sending login')
    #
    def get_status(self):
        '''
        Returns helpful messages that lets its parent class understand
        what state it is in.
        '''
        return self.status.name
    def attempt_connection(self, addr, port, username, password, cb_connect, cb_condrop):
        '''
        The reason for the callbacks is because the class that this is
        emcapsulated within will probably want to log that activity.
        Moreover, if there is a connection abort, they may wish to take
        corrective action.
        '''
        self.cb_connect = cb_connect
        self.cb_condrop = cb_condrop
        self._set_login_credentials(
            username=username,
            password=password)
        self.engine.open_tcp_client(
            addr=addr,
            port=port,
            cb_tcp_connect=self._engine_on_tcp_connect,
            cb_tcp_condrop=self._engine_on_tcp_condrop,
            cb_tcp_recv=self._engine_on_tcp_recv)
        self.status = ClientStatus.attempting_tcp_connection
    #
    def _engine_on_tcp_connect(self, cs_tcp_connect):
        engine = cs_tcp_connect.engine
        client_sid = cs_tcp_connect.client_sid
        addr = cs_tcp_connect.addr
        port = cs_tcp_connect.port
        #
        self.cb_connect(
            cs_tcp_connect=cs_tcp_connect)
        self.status = ClientStatus.ready_to_attempt_login
    def _engine_on_tcp_condrop(self, cs_tcp_condrop):
        engine = cs_tcp_condrop.engine
        client_sid = cs_tcp_condrop.client_sid
        message = cs_tcp_condrop.message
        #
        while self.q_received:
            self.q_received.pop()
        self.cb_condrop(cs_tcp_condrop)
        self.status = ClientStatus.dormant
    def _engine_on_tcp_recv(self, cs_tcp_recv):
        engine = cs_tcp_recv.engine
        client_sid = cs_tcp_recv.client_sid
        data = cs_tcp_recv.data
        #
        self.q_received.append(data)
        engine.send(
            sid=client_sid,
            data='q_received %s\n'%len(data))
    #
    def _set_login_credentials(self, username, password):
        self.login_credentials.username = username
        self.login_credentials.password = password
    def _attempt_login(self):
        arr = self.gruel_press.create_client_login_payload(
            username=self.login_credentials.username,
            password=self.login_credentials.password)
        self.engine.send(
            sid=self.client_sid,
            data=arr)
        self.status = ClientStatus.login_message_in_flight

def prop_gruel_client_new(engine, gruel_press, gruel_puff):
    ob = PropGruelClient(
        engine=engine,
        gruel_press=gruel_press,
        gruel_puff=gruel_puff)
    return ob

