#
# prop_gruel_server
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

from .gruel_schema import GruelMessageType
from .gruel_schema import gmt_value_to_name

from solent.log import log
from solent.log import hexdump_bytearray
from solent.util import ns
from solent.util import uniq
from solent.eng import gruel_press_new

from collections import deque
from collections import OrderedDict as od
from enum import Enum

class ServerStatus(Enum):
    stopped = uniq()
    listening = uniq()
    tcp_up_awaiting_login = uniq()
    authorised_connection = uniq()
    # on a bad logon, we want to sleep a bit before we kick people. This
    # impedes brute-force attacks. This mode is for when we are in that
    # in between time when we are going to boot someone but haven't yet.
    preparing_to_boot = uniq()

class PropGruelServer:
    def __init__(self, engine, gruel_press, gruel_puff):
        self.engine = engine
        self.gruel_press = gruel_press
        self.gruel_puff = gruel_puff
        #
        self.status = ServerStatus.stopped
        self.server_addr = None
        self.server_port = None
        self.server_username = None
        self.server_password = None
        self.server_sid = None
        self.cb_tcp_connect = None
        self.cb_tcp_condrop = None
        self.cb_doc_recv = None
        self.client_sid = None
        #
        self.t_boot = None
        self.boot_message = None
    def get_status(self):
        return self.status.name
    def at_turn(self, activity):
        pass
    def activate(self, addr, port, username, password, cb_tcp_connect, cb_tcp_condrop, cb_doc):
        self.server_addr = addr
        self.server_port = port
        self.server_username = username
        self.server_password = password
        #
        if self.status != ServerStatus.stopped:
            raise Exception('server is not currently stopped')
        #
        self.cb_tcp_connect = cb_tcp_connect
        self.cb_tcp_condrop = cb_tcp_condrop
        self.cb_doc = cb_doc
        #
        self._raise_server()
        self.status = ServerStatus.listening
    def stop(self):
        if self.status == ServerStatus.stopped:
            raise Exception('server is already stopped')
            return
        if self.status == ServerStatus.listening:
            self.engine.close_tcp_server(
                sid=self.server_sid)
            self.server_sid = None
            self.server_addr = None
            self.server_port = None
            self.t_boot = None
            self.boot_message = None
            self.status = ServerStatus.stopped
            return
        if self.status == ServerStatus.tcp_up_awaiting_login:
            self.engine.close_tcp_client(
                sid=self.client_sid)
            self.client_sid = None
            self.server_addr = None
            self.server_port = None
            self.t_boot = None
            self.boot_message = None
            self.status = ServerStatus.stopped
            return
        raise Exception('status %s not handled'%(self.status.name))
    #
    def _engine_on_tcp_connect(self, cs_tcp_connect):
        engine = cs_tcp_connect.engine
        client_sid = cs_tcp_connect.client_sid
        addr = cs_tcp_connect.addr
        port = cs_tcp_connect.port
        #
        self.client_sid = client_sid
        self.engine.close_tcp_server(
            sid=self.server_sid)
        self.server_sid = None
        self.status = ServerStatus.tcp_up_awaiting_login
        #
        self.cb_tcp_connect(
            cs_tcp_connect=cs_tcp_connect)
    def _engine_on_tcp_condrop(self, cs_tcp_condrop):
        engine = cs_tcp_condrop.engine
        client_sid = cs_tcp_condrop.client_sid
        message = cs_tcp_condrop.message
        #
        self.client_sid = None
        self._raise_server()
        self.status = ServerStatus.listening
        #
        self.cb_tcp_condrop(
            cs_tcp_condrop=cs_tcp_condrop)
    def _engine_on_tcp_recv(self, cs_tcp_recv):
        engine = cs_tcp_recv.engine
        client_sid = cs_tcp_recv.client_sid
        data = cs_tcp_recv.data
        #
        d_message = self.gruel_puff.unpack(
            payload=data)
        if self.status == ServerStatus.stopped:
            raise Exception("should not happen")
        elif self.status == ServerStatus.listening:
            raise Exception("should not happen")
        elif self.status == ServerStatus.tcp_up_awaiting_login:
            if d_message['message_h'] != 'client_login':
                log('WEIRD: client is not logged in but sending %s'%(
                    d_message['message_h']))
                self._move_to_boot(
                    message='not logged in')
                return
            if d_message['username'] != self.server_username:
                log('Invalid credentials')
                self._move_to_boot(
                    message='invalid credentials')
                return
            if d_message['password'] != self.server_password:
                log('Invalid credentials')
                self._move_to_boot(
                    message='invalid credentials')
                return
            self.status = ServerStatus.authorised_connection
        elif self.status == ServerStatus.authorised_connection:
            if d_message['message_h'] == 'heartbeat':
                raise Exception('xxx')
            if d_message['message_h'] == 'client_login':
                log('WEIRD: client already logged in.')
                self._move_to_boot(
                    message="Was already logged in, pls don't be weird")
                return
            if d_message['message_h'] == 'doc_data':
                raise Exception('xxx')
        elif self.status == ServerStatus.pausing_to_boot:
            # we don't care about anything the client has to say in this
            # case. they'll be booted regardless.
            return
    # on a bad logon, we want to sleep a bit before we kick people. This
    # impedes brute-force attacks. This mode is for when we are in that
    # in between time when we are going to boot someone but haven't yet.
    pausing_to_boot = uniq()
    #
    def _raise_server(self):
        self.server_sid = self.engine.open_tcp_server(
            addr=self.server_addr,
            port=self.server_port,
            cb_tcp_connect=self._engine_on_tcp_connect,
            cb_tcp_condrop=self._engine_on_tcp_condrop,
            cb_tcp_recv=self._engine_on_tcp_recv)
    def _move_to_boot(self, message):
        log('Preparing to boot (%s)'%(message))
        self.status = ServerStatus.preparing_to_boot
        self.t_boot = self.engine.get_clock().now() + 3
        self.boot_message = message

def prop_gruel_server_new(engine, gruel_press, gruel_puff):
    ob = PropGruelServer(
        engine=engine,
        gruel_press=gruel_press,
        gruel_puff=gruel_puff)
    return ob

