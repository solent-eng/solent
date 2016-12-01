#
# prop_gruel_server
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

from .server.tcp_server_cog import tcp_server_cog_new

from solent.log import log
from solent.log import hexdump_bytearray
from solent.util import ns
from solent.util import uniq
from solent.eng import gruel_press_new
from solent.eng import nearcast_orb_new
from solent.eng import nearcast_schema_new

from collections import deque
from collections import OrderedDict as od
from enum import Enum

I_NEARCAST_GRUEL_SERVER = '''
    i message h
        i field h

    message nearnote
        field s

    message valid_ip
        field ip

    message all_ips_are_valid

    message start_service
        field addr
        field port
        field username
        field password

    message stop_service

    message announce_client_connect
        field ip
        field port

    message announce_client_condrop

    message boot_client
        field seconds_to_wait
        field message

    # A message from the client that has not yet been through the login cog.
    # Once a TCP connection is done, all activity should flow to the login
    # cog, which should act as a gateway.
    message suspect_client_message
        field d_gruel

    message authorised_client_message
        field d_gruel

    message outgoing_message_settings
        field max_packet_size
        field max_doc_size

    message inbound_heartbeat

    message outbound_heartbeat

    message outbound_document
        field doc_h
        field doc

'''

class UplinkCog:
    def __init__(self, cog_h, orb, engine, cb_nearnote):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        self.cb_nearnote = cb_nearnote
    #
    def on_nearnote(self, s):
        self.cb_nearnote(
            s=s)
    #
    def send_nearnote(self, s):
        self.orb.nearcast(
            cog_h=self.cog_h,
            message_h='nearnote',
            s=s)
    def send_start_service(self, addr, port, username, password):
        self.orb.nearcast(
            cog_h=self.cog_h,
            message_h='start_service',
            addr=addr,
            port=port,
            username=username,
            password=password)
    def send_stop_service(self):
        self.orb.nearcast(
            cog_h=self.cog_h,
            message_h='stop_service')

class PropGruelServer:
    def __init__(self, engine, cb_nearnote, cb_client_doc):
        self.engine = engine
        self.cb_nearnote = None
        self.cb_client_doc = None
        #
        self.b_active = False
        #
        self.gruel_server_nearcast = nearcast_orb_new(
            engine=self.engine,
            nearcast_schema=nearcast_schema_new(
                i_nearcast=I_NEARCAST_GRUEL_SERVER))
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
            engine=engine,
            cb_nearnote=cb_nearnote)
        self.gruel_server_nearcast.add_cog(
            cog=self.uplink)
        #
        self.uplink.send_nearnote(
            s='prop_gruel_server: nearcast_started')
    def at_turn(self, activity):
        self.gruel_server_nearcast.at_turn(
            activity=activity)
    #
    def get_status(self):
        return self.b_active
    def start(self, addr, port, username, password):
        if self.b_active:
            raise Exception('server is already started')
        #
        self.uplink.send_start_service(
            addr=addr,
            port=port,
            username=username,
            password=password)
        self.b_active = True
    def stop(self):
        if not self.b_active:
            raise Exception('server is already stopped')
            return
        #
        self.uplink.send_stop_service()
        self.b_active = False

def prop_gruel_server_new(engine, cb_nearnote, cb_client_doc):
    ob = PropGruelServer(
        engine=engine,
        cb_nearnote=cb_nearnote,
        cb_client_doc=cb_client_doc)
    return ob

