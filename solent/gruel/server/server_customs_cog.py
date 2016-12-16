#
# server_customs_cog
#
# // further work
# The logic around max_fulldoc_size is not implemented.
#
# // overview
# This is the main workhorse and clearing-yard for the server side of the
# gruel protocol. All intent to send a gruel must pass through this. All
# incoming gruel must pass through this. This class ensures that only
# authorised activity gets into the system, and it's responsible for
# splitting outgoing documents into sensible parcels.
#
# If we didn't have this class, we'd have to mix up all this business logic
# with the TCP server.
#
# The reason for the name 'customs' is in the spirit of national border
# enforcement. We don't trust anything that's coming in until we checked it
# through customs. (And thereby prevent unauthorised packets from being
# processed)
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

from solent.gruel import gruel_press_new
from solent.gruel import gruel_schema_new
from solent.gruel.gruel_schema import DOCPART_OVERHEAD
from solent.gruel.gruel_schema import GruelMessageType
from solent.log import log
from solent.util import uniq

from collections import deque
from enum import Enum

class ServerCustomsState(Enum):
    #
    # we sit on this state when we have a clear slate
    awaiting_login = uniq()
    authorised = uniq()
    #
    # when we decide to kick someone, the first thing we do is to sleep
    # on it for a bit, so that they can't sit there and spam us with
    # reconnects. this state handles that
    reject_stage_a = uniq()
    #
    # after a bit, we send them a message telling them why we're booting them
    # and then we sleep for a little bit more
    reject_stage_b = uniq()
    #
    # this is for after we've booted them.
    rejected = uniq()

def create_d(**kwargs):
    return kwargs

class ServerCustomsCog:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        # long-lived variables
        self.expected_password = None
        self.gruel_schema = gruel_schema_new()
        self.gruel_press = gruel_press_new(
            gruel_schema=self.gruel_schema,
            mtu=engine.mtu)
        #
        # variables that are zeroed between each client session
        self.state = ServerCustomsState.awaiting_login
        self.max_fulldoc_size = None
        self.max_packet_size = None
        self.max_docpart_size = None
        self.reject_clock_time = None
        self.reject_message = None
        self.recv_doc_buffer = None
        self.send_doc_q = deque()
    def _zero(self):
        """
        Resets the state between client connections.
        """
        self.state = ServerCustomsState.awaiting_login
        self.max_fulldoc_size = None
        self.max_packet_size = None
        self.max_docpart_size = None
        self.reject_clock_time = None
        self.reject_message = None
        self.recv_doc_buffer = []
        self.send_doc_q.clear()
        #
        self.nc_nearnote(
            s='clearing state')
    #
    def at_turn(self, activity):
        if self.state == ServerCustomsState.reject_stage_a:
            # We sit on a plan to reject for several seconds. this
            # prevents users from spamming us with bad logons. After
            # three seconds, we send a reject message, and move to the
            # reject state b.
            now = self.engine.get_clock().now()
            if now >= self.reject_clock_time + 3:
                activity.mark(
                    l=self,
                    s='preparing server_bye')
                self.nc_gruel_send(
                    payload=self.gruel_press.create_server_bye_payload(
                        notes=self.reject_message))
                self.state = ServerCustomsState.reject_stage_b
        elif self.state == ServerCustomsState.reject_stage_b:
            # After a further second, then we then ask for a tcp boot
            now = self.engine.get_clock().now()
            if now >= self.reject_clock_time + 4:
                activity.mark(
                    l=self,
                    s='requesting boot')
                self.nc_please_tcp_boot()
                self.state = ServerCustomsState.rejected
        elif self.state == ServerCustomsState.authorised:
            if self.send_doc_q:
                activity.mark(
                    l=self,
                    s='preparing docpart')
                data = self.send_doc_q.popleft()
                b_complete = 1
                if len(data) > self.max_docpart_size:
                    self.send_doc_q.appendleft(
                        data[self.max_docpart_size:])
                    data = data[:self.max_docpart_size]
                    b_complete = 0
                self.nc_gruel_send(
                    payload=self.gruel_press.create_docdata_payload(
                        data=data,
                        b_complete=b_complete))
    def on_announce_tcp_connect(self, ip, port):
        self._zero()
    def on_announce_tcp_condrop(self):
        self._zero()
    def on_start_service(self, ip, port, password):
        self.expected_password = password
    def on_gruel_recv(self, d_gruel):
        if None == self.expected_password:
            raise Exception("Alg exception. Expected password is empty.")
        message_h = d_gruel['message_h']
        if self.state == ServerCustomsState.awaiting_login:
            if message_h != 'client_login':
                log('expected client_login but got %s'%(message_h))
                self._to_rejection(
                    s='expected login message first')
                return
            self._attempt_to_handle_login(
                d_gruel=d_gruel)
        elif self.state == ServerCustomsState.authorised:
            if message_h == 'client_login':
                self._to_rejection(
                    s='it is invalid to log in twice')
                return
            elif message_h == 'server_greet':
                self._to_rejection('client sent server_greet. invalid.')
                return
            elif message_h == 'server_bye':
                self._to_rejection('client sent server_bye. invalid.')
                return
            elif message_h == 'heartbeat':
                self.nc_heartbeat_recv()
            elif message_h == 'docdata':
                b_complete = d_gruel['b_complete']
                data = d_gruel['data']
                #
                self.recv_doc_buffer.append(data)
                if b_complete == 1:
                    doc = ''.join(self.recv_doc_buffer)
                    self.recv_doc_buffer = []
                    self.nc_doc_recv(
                        doc=doc)
                return
            else:
                raise Exception('xxx')
        else:
            log('Currently disconnecting client. Ignoring %s.'%message_h)
            return
    def on_doc_send(self, doc):
        if self.max_fulldoc_size != None:
            if len(doc) > self.max_fulldoc_size:
                # Haven't worked out what to do in this situation. It is
                # caused by us trying to send a packet that is larger than
                # what the client is set up to handle. Maybe we need to
                # call back to our application when the client sets a max
                # doc size so we know. Not sure.
                raise Exception('xxx')
        self.send_doc_q.append(doc)
    def on_heartbeat_send(self):
        self.nc_gruel_send(
            payload=self.gruel_press.create_heartbeat_payload())
    #
    def _to_rejection(self, s):
        self.state = ServerCustomsState.reject_stage_a
        self.reject_clock_time = self.engine.get_clock().now()
        self.reject_message = s
    def _attempt_to_handle_login(self, d_gruel):
        if d_gruel['password'] != self.expected_password:
            self._to_rejection(
                s='bad login')
            return
        #
        # ok: this looks like a valid login. now we have to massage our
        # figures for document and payload sizes.
        self.max_fulldoc_size = d_gruel['max_fulldoc_size']
        if 0 == self.max_fulldoc_size:
            self.max_fulldoc_size = None
        elif self.max_fulldoc_size < 400:
            self._to_rejection(
                s='ludicrously small doc size.')
            return
        #
        self.max_packet_size = d_gruel['max_packet_size']
        if 0 == self.max_packet_size:
            self.max_packet_size = self.engine.mtu
        elif self.max_packet_size < 400:
            self._to_rejection(
                s='unreasonably small packet size.')
            return
        elif self.max_packet_size > self.engine.mtu:
            self.max_packet_size = self.engine.mtu
        #
        self.max_docpart_size = self.max_packet_size - DOCPART_OVERHEAD
        # announce and confirm this successful login
        self.nc_announce_login(
            max_packet_size=0,
            max_fulldoc_size=0)
        self.nc_gruel_send(
            payload=self.gruel_press.create_server_greet_payload(
                max_packet_size=1234))
        self.state = ServerCustomsState.authorised
        return
    #
    def nc_nearnote(self, s):
        self.orb.nearcast(
            cog=self,
            message_h='nearnote',
            s=s)
    def nc_announce_login(self, max_packet_size, max_fulldoc_size):
        self.orb.nearcast(
            cog=self,
            message_h='announce_login',
            max_packet_size=max_packet_size,
            max_fulldoc_size=max_fulldoc_size)
    def nc_please_tcp_boot(self):
        self.orb.nearcast(
            cog=self,
            message_h='please_tcp_boot')
    def nc_gruel_send(self, payload):
        self.orb.nearcast(
            cog=self,
            message_h='gruel_send',
            payload=payload)
    def nc_doc_recv(self, doc):
        self.orb.nearcast(
            cog=self,
            message_h='doc_recv',
            doc=doc)
    def nc_heartbeat_recv(self):
        self.orb.nearcast(
            cog=self,
            message_h='heartbeat_recv')

def server_customs_cog_new(cog_h, orb, engine):
    ob = ServerCustomsCog(
        cog_h=cog_h,
        orb=orb,
        engine=engine)
    return ob

