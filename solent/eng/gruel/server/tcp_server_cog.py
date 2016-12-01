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

from solent.eng import ip_validator_new
from solent.eng.gruel.gruel_schema import gruel_schema_new
from solent.eng.gruel.gruel_press import gruel_press_new
from solent.eng.gruel.gruel_puff import gruel_puff_new
from solent.log import log

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
        self.server_sid = None
        self.client_sid = None
        self.ip_validator = ip_validator_new()
        #
        self.server_addr = None
        self.server_port = None
    #
    def on_all_ips_are_valid(self):
        self.ip_validator.accept_any_ip()
    def on_valid_ip(self, ip):
        self.ip_validator.add_ip(
            ip=ip)
    def on_start_service(self, addr, port, username, password):
        if self.server_sid != None:
            log('weird: already listening to server (%s)'%self.server_sid)
            raise Exception('algorithm exception')
        if self.client_sid != None:
            log('weird: client connectied')
            raise Exception('algorithm exception')
        self._engine_raise_server()
    def on_stop_service(self):
        self._engine_lower_any_server()
        self._engine_boot_any_client()
        self.ncsend_nearnote('stopped')
    #
    def ncsend_nearnote(self, s):
        self.orb.nearcast(
            cog_h=self.cog_h,
            message_h='nearnote',
            s='tcp_server_cog: %s'%s,)
    def ncsend_suspect_client_message(self, d_gruel):
        self.orb.nearcast(
            cog_h=self.cog_h,
            message_h='suspect_client_message',
            d_gruel=d_gruel)
    #
    def _engine_raise_server(self):
        self.server_sid = self.engine.open_tcp_server(
            addr=self.server_addr,
            port=self.server_port,
            cb_tcp_connect=self._engine_on_tcp_connect,
            cb_tcp_condrop=self._engine_on_tcp_condrop,
            cb_tcp_recv=self._engine_on_tcp_recv)
        self.ncsend_nearnote('listening')
    def _engine_lower_any_server(self):
        if self.server_sid == None:
            return
        self.engine.close_tcp_server(
            sid=self.server_sid)
        self.server_sid = None
    def _engine_boot_any_client(self):
        if self.client_sid == None:
            return
        self.ncsend_nearnote('booting_client')
        self.engine.close_tcp_client(
            sid=self.client_sid)
        self.client_sid = None
    def _engine_on_tcp_connect(self, cs_tcp_connect):
        engine = cs_tcp_connect.engine
        client_sid = cs_tcp_connect.client_sid
        addr = cs_tcp_connect.addr
        port = cs_tcp_connect.port
        #
        if not self.ip_validator.is_ok(addr):
            self.engine.close_tcp_client(
                sid=client_sid)
            self.ncsend_nearnote('invalid_ip/%s:%s'%(addr, port))
            return
        #
        self.ncsend_nearnote('client_connect/%s:%s'%(addr, port))
        self._engine_lower_any_server()
        self.client_sid = client_sid
    def _engine_on_tcp_condrop(self, cs_tcp_condrop):
        engine = cs_tcp_condrop.engine
        client_sid = cs_tcp_condrop.client_sid
        message = cs_tcp_condrop.message
        #
        self.ncsend_nearnote('client condrop')
        #
        self.client_sid = None
        self._engine_raise_server()
    def _engine_on_tcp_recv(self, cs_tcp_recv):
        engine = cs_tcp_recv.engine
        client_sid = cs_tcp_recv.client_sid
        data = cs_tcp_recv.data
        #
        # we unpack the message and broadcast it so that the login
        # server can look at it
        d_gruel = self.gruel_puff.unpack(
            payload=data)
        self.ncsend_suspect_client_message(
            d_gruel=d_gruel)

def tcp_server_cog_new(cog_h, orb, engine):
    ob = TcpServerCog(
        cog_h=cog_h,
        orb=orb,
        engine=engine)
    return ob

