#
# spin_gruel_server
#
# // overview
# At the obvious level, this provides an abstraction that you can use to
# create a server for gruel protocol.
#
# It also serves a demonstration of the way you can use nearcasting to build a
# subsystem that has complex needs, whilst keeping the code simple.
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

from .gs_nearcast_schema import gs_nearcast_schema_new
from .ipval_cog import ipval_cog_new
from .heartbeater_cog import heartbeater_cog_new
from .server_customs_cog import server_customs_cog_new
from .tcp_server_cog import tcp_server_cog_new

from solent.eng import orb_new
from solent.gruel import gruel_press_new
from solent.log import hexdump_bytes
from solent.log import log
from solent.util import ns
from solent.util import uniq

from collections import deque
from collections import OrderedDict as od
from enum import Enum

class UplinkCog:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
    #
    def nc_nearnote(self, s):
        self.orb.nearcast(
            cog=self,
            message_h='nearnote',
            s=s)
    def nc_start_service(self, addr, port, password):
        self.orb.nearcast(
            cog=self,
            message_h='start_service',
            ip=addr,
            port=port,
            password=password)
    def nc_ipval_add_ip(self, ip):
        self.orb.nearcast(
            cog=self,
            message_h='ipval_add_ip',
            ip=ip)
    def nc_doc_send(self, doc):
        self.orb.nearcast(
            cog=self,
            message_h='doc_send',
            doc=doc)
    def nc_stop_service(self):
        self.orb.nearcast(
            cog=self,
            message_h='stop_service')

class SpinGruelServer:
    def __init__(self, engine, cb_doc_recv):
        self.engine = engine
        self.cb_doc_recv = cb_doc_recv
        #
        self.b_active = False
        #
        self.orb = engine.init_orb(
            orb_h=__name__,
            nearcast_schema=gs_nearcast_schema_new())
        self.orb.add_log_snoop()
        #
        # disabled because it distracts from development
        #self.orb.init_cog(heartbeater_cog_new)
        self.orb.init_cog(ipval_cog_new)
        self.orb.init_cog(server_customs_cog_new)
        self.orb.init_cog(tcp_server_cog_new)
        self.orb.init_cog(UplinkCog)
        #
        self.uplink = self.orb.init_cog(UplinkCog)
        #
        self.uplink.nc_nearnote(
            s='spin_gruel_server: nearcast_started')
    def at_turn(self, activity):
        self.orb.at_turn(
            activity=activity)
    #
    def get_status(self):
        return self.b_active
    def start(self, addr, port, password):
        if self.b_active:
            log('ERROR: server is already started')
            return
        #
        self.uplink.nc_start_service(
            addr=addr,
            port=port,
            password=password)
        self.b_active = True
    def enable_ip(self, ip):
        self.uplink.nc_ipval_add_ip(
            ip=ip)
    def send_doc(self, doc):
        self.uplink.nc_doc_send(
            doc=doc)
    def stop(self):
        if not self.b_active:
            log('ERROR: server is already stopped')
            return
        #
        self.uplink.nc_stop_service()
        self.b_active = False
    #
    def on_doc_recv(self, doc):
        self.cb_doc_recv(
            doc=doc)

def spin_gruel_server_new(engine, cb_doc_recv):
    ob = SpinGruelServer(
        engine=engine,
        cb_doc_recv=cb_doc_recv)
    return ob

