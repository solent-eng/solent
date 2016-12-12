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

from solent.gruel.gruel_schema import gruel_schema_new
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
        self.gruel_schema = gruel_schema_new()
        self.gruel_press = gruel_press_new(
            gruel_schema=self.gruel_schema,
            mtu=engine.mtu)
        self.gruel_puff = gruel_puff_new(
            gruel_schema=self.gruel_schema,
            mtu=engine.mtu)
        #
        self.b_active = False
        self.server_sid = None
        self.client_sid = None
        #
        self.server_addr = None
        self.server_port = None
    #
    def on_start_service(self, ip, port, password):
        if self.server_sid != None:
            log('weird: already listening to server (%s)'%self.server_sid)
            raise Exception('algorithm exception')
        if self.client_sid != None:
            log('weird: client connectied')
            raise Exception('algorithm exception')
        self.server_addr = ip
        self.server_port = port
        self._engine_raise_server()
        self.b_active = True
    def on_stop_service(self):
        self._engine_lower_any_server()
        self._engine_boot_any_client()
        self.b_active = False
    def on_please_tcp_boot(self):
        self._engine_boot_any_client()
        # at_turn will take care of bringing the server back
    def on_gruel_send(self, payload):
        if not self.client_sid:
            return
        self.engine.send(
            sid=self.client_sid,
            payload=payload)
    def at_turn(self, activity):
        if self.b_active:
            if self.server_sid == None and self.client_sid == None:
                activity.mark(
                    l=self,
                    s='restarting server (probably after disconnect)')
                self._engine_raise_server()
    #
    def nc_announce_tcp_connect(self, ip, port):
        self.orb.nearcast(
            cog=self,
            message_h='announce_tcp_connect',
            ip=ip,
            port=port)
    def nc_announce_tcp_condrop(self):
        self.orb.nearcast(
            cog=self,
            message_h='announce_tcp_condrop')
    def nc_gruel_recv(self, d_gruel):
        self.orb.nearcast(
            cog=self,
            message_h='gruel_recv',
            d_gruel=d_gruel)
    def nc_please_tcp_boot(self):
        self.orb.nearcast(
            cog=self,
            message_h='please_tcp_boot')
    #
    def _engine_raise_server(self):
        self.server_sid = self.engine.open_tcp_server(
            addr=self.server_addr,
            port=self.server_port,
            cb_tcp_connect=self._engine_on_tcp_connect,
            cb_tcp_condrop=self._engine_on_tcp_condrop,
            cb_tcp_recv=self._engine_on_tcp_recv)
    def _engine_lower_any_server(self):
        if self.server_sid == None:
            return
        self.engine.close_tcp_server(
            sid=self.server_sid)
        self.server_sid = None
    def _engine_boot_any_client(self):
        if self.client_sid == None:
            return
        self.engine.close_tcp_client(
            sid=self.client_sid)
        self.client_sid = None
    def _engine_on_tcp_connect(self, cs_tcp_connect):
        engine = cs_tcp_connect.engine
        client_sid = cs_tcp_connect.client_sid
        addr = cs_tcp_connect.addr
        port = cs_tcp_connect.port
        #
        self.nc_announce_tcp_connect(
            ip=addr,
            port=port)
        self.client_sid = client_sid
        self._engine_lower_any_server()
    def _engine_on_tcp_condrop(self, cs_tcp_condrop):
        engine = cs_tcp_condrop.engine
        client_sid = cs_tcp_condrop.client_sid
        message = cs_tcp_condrop.message
        #
        self.nc_announce_tcp_condrop()
        self.client_sid = None
    def _engine_on_tcp_recv(self, cs_tcp_recv):
        engine = cs_tcp_recv.engine
        client_sid = cs_tcp_recv.client_sid
        data = cs_tcp_recv.data
        #
        # we unpack the message and broadcast it so that the login
        # server can look at it
        try:
            d_gruel = self.gruel_puff.unpack(
                payload=data)
            self.nc_gruel_recv(
                d_gruel=d_gruel)
        except:
            log('Could not parse payload. Likely protocol error.')
            self.nc_please_tcp_boot()

def tcp_server_cog_new(cog_h, orb, engine):
    ob = TcpServerCog(
        cog_h=cog_h,
        orb=orb,
        engine=engine)
    return ob

