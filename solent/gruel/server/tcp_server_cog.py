#
# tcp_server_cog
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

from solent.gruel.gruel_protocol import gruel_protocol_new
from solent.gruel.gruel_press import gruel_press_new
from solent.gruel.gruel_puff import gruel_puff_new
from solent.log import log

import traceback

class TcpServerCog:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.gruel_protocol = gruel_protocol_new()
        self.gruel_press = gruel_press_new(
            gruel_protocol=self.gruel_protocol,
            mtu=engine.mtu)
        self.gruel_puff = gruel_puff_new(
            gruel_protocol=self.gruel_protocol,
            mtu=engine.mtu)
        #
        self.b_active = False
        self.server_sid = None
        self.accept_sid = None
        #
        self.server_addr = None
        self.server_port = None
    def at_turn(self, activity):
        pass
    def at_close(self):
        self.close_everything()
    #
    def on_start_service(self, ip, port, password):
        if self.server_sid != None:
            log('weird: already listening to server (%s)'%self.server_sid)
            raise Exception('algorithm exception')
        if self.accept_sid != None:
            log('weird: accept connectied')
            raise Exception('algorithm exception')
        self.server_addr = ip
        self.server_port = port
        self._start_server()
        self.b_active = True
    def on_stop_service(self):
        self.close_everything()
    def on_please_tcp_boot(self):
        self._boot_any_accept()
        # at_turn will take care of bringing the server back
    def on_gruel_send(self, bb):
        if not self.accept_sid:
            return
        self.engine.send(
            sid=self.accept_sid,
            bb=bb)
    #
    def _boot_any_accept(self):
        if self.accept_sid != None:
            self.engine.close_tcp_accept(
                accept_sid=self.accept_sid)
    def _boot_any_server(self):
        if self.server_sid != None:
            self.engine.close_tcp_server(
                server_sid=self.server_sid)
            self.server_sid = None
    def _engine_on_tcp_accept_connect(self, cs_tcp_accept_connect):
        engine = cs_tcp_accept_connect.engine
        server_sid = cs_tcp_accept_connect.server_sid
        accept_sid = cs_tcp_accept_connect.accept_sid
        client_addr = cs_tcp_accept_connect.client_addr
        client_port = cs_tcp_accept_connect.client_port
        #
        self.nearcast.announce_tcp_connect(
            ip=client_addr,
            port=client_port)
        self.accept_sid = accept_sid
        self._boot_any_server()
    def _engine_on_tcp_accept_condrop(self, cs_tcp_accept_condrop):
        engine = cs_tcp_accept_condrop.engine
        accept_sid = cs_tcp_accept_condrop.accept_sid
        message = cs_tcp_accept_condrop.message
        #
        self.nearcast.announce_tcp_condrop()
        self.accept_sid = None
        if self.b_active:
            self._start_server()
    def _engine_on_tcp_accept_recv(self, cs_tcp_accept_recv):
        engine = cs_tcp_accept_recv.engine
        accept_sid = cs_tcp_accept_recv.accept_sid
        bb = cs_tcp_accept_recv.bb
        #
        # we unpack the message and broadcast it so that the login
        # server can look at it
        try:
            d_gruel = self.gruel_puff.unpack(
                bb=bb)
            self.nearcast.gruel_recv(
                d_gruel=d_gruel)
        except:
            log('Could not parse bb. Likely protocol error.')
            self.nearcast.please_tcp_boot()
    def _engine_on_tcp_server_start(self, cs_tcp_server_start):
        engine = cs_tcp_server_start.engine
        server_sid = cs_tcp_server_start.server_sid
        addr = cs_tcp_server_start.addr
        port = cs_tcp_server_start.port
        #
        self.server_sid = server_sid
    def _engine_on_tcp_server_stop(self, cs_tcp_server_stop):
        engine = cs_tcp_server_stop.engine
        server_sid = cs_tcp_server_stop.server_sid
        message = cs_tcp_server_stop.message
        #
        self.server_sid = server_sid
    def _start_server(self):
        self.engine.open_tcp_server(
            addr=self.server_addr,
            port=self.server_port,
            cb_tcp_accept_connect=self._engine_on_tcp_accept_connect,
            cb_tcp_accept_condrop=self._engine_on_tcp_accept_condrop,
            cb_tcp_accept_recv=self._engine_on_tcp_accept_recv,
            cb_tcp_server_start=self._engine_on_tcp_server_start,
            cb_tcp_server_stop=self._engine_on_tcp_server_stop)
    #
    def close_everything(self):
        self.b_active = False
        self._boot_any_server()
        self._boot_any_accept()
    def is_server_listening(self):
        return self.server_sid != None
    def is_accept_connected(self):
        return self.accept_sid != None

def tcp_server_cog_new(cog_h, orb, engine):
    ob = TcpServerCog(
        cog_h=cog_h,
        orb=orb,
        engine=engine)
    return ob

