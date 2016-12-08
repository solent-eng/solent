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
from .tcp_server_cog import tcp_server_cog_new

from solent.eng import orb_new
from solent.eng import log_snoop_new
from solent.gruel import gruel_press_new
from solent.log import hexdump_bytearray
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
    def send_nearnote(self, s):
        self.orb.nearcast(
            cog_h=self.cog_h,
            message_h='nearnote',
            s=s)
    def send_start_service(self, addr, port, password):
        self.orb.nearcast(
            cog_h=self.cog_h,
            message_h='start_service',
            ip=addr,
            port=port,
            password=password)
    def send_stop_service(self):
        self.orb.nearcast(
            cog_h=self.cog_h,
            message_h='stop_service')

class SpinGruelServer:
    def __init__(self, engine, cb_doc_recv):
        self.engine = engine
        self.cb_doc_recv = cb_doc_recv
        #
        self.b_active = False
        #
        self.nearcast_schema = gs_nearcast_schema_new()
        snoop = log_snoop_new(
            nearcast_schema=self.nearcast_schema)
        self.gruel_server_nearcast = orb_new(
            engine=self.engine,
            nearcast_schema=self.nearcast_schema,
            snoop=snoop)
        #
        self.tcp_server_cog = tcp_server_cog_new(
            cog_h='tcp_server_cog',
            orb=self.gruel_server_nearcast,
            engine=engine)
        self.gruel_server_nearcast.add_cog(
            cog=self.tcp_server_cog)
        #
        self.uplink = UplinkCog(
            cog_h='uplink',
            orb=self.gruel_server_nearcast,
            engine=engine)
        self.gruel_server_nearcast.add_cog(
            cog=self.uplink)
        #
        self.uplink.send_nearnote(
            s='spin_gruel_server: nearcast_started')
    def at_turn(self, activity):
        self.gruel_server_nearcast.at_turn(
            activity=activity)
    #
    def get_status(self):
        return self.b_active
    def start(self, addr, port, password):
        if self.b_active:
            log('ERROR: server is already started')
            return
        #
        self.uplink.send_start_service(
            addr=addr,
            port=port,
            password=password)
        self.b_active = True
    def stop(self):
        if not self.b_active:
            log('ERROR: server is already stopped')
            return
        #
        self.uplink.send_stop_service()
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

