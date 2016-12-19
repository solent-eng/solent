#
# spin_gruel_client
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
from solent.gruel.gruel_schema import GruelMessageType
from solent.gruel.gruel_schema import gmt_value_to_name
from solent.log import log
from solent.log import hexdump_bytes
from solent.util import ns
from solent.util import uniq

from collections import deque
from collections import OrderedDict as od
from enum import Enum

class ClientStatus(Enum):
    dormant = uniq()
    attempting_tcp_connection = uniq()
    ready_to_attempt_login = uniq()
    login_message_in_flight = uniq()
    streaming = uniq()

class SpinGruelClient:
    def __init__(self, engine, gruel_press, gruel_puff):
        self.engine = engine
        self.gruel_press = gruel_press
        self.gruel_puff = gruel_puff
        #
        self.status = ClientStatus.dormant
        #
        self.login_credentials = ns()
        self.max_packet_size = self.engine.mtu
        self.heartbeat_interval = 4
        self.last_heartbeat_recv = None
        self.last_heartbeat_sent = None
        self.q_outbound_documents = deque()
        #
        # form: (addr, port) : deque containing data
        self.cb_connect = None
        self.cb_condrop = None
        self.cb_doc = None
        self.doc_accumulator = None
        self.client_sid = None
    def at_turn(self, activity):
        if self.status == ClientStatus.dormant:
            return

        if self.status == ClientStatus.ready_to_attempt_login:
            self._attempt_login()
            activity.mark(
                l=self.__class__.__name__,
                s='sending login')
            return

        if self.status == ClientStatus.attempting_tcp_connection:
            return

        next_heartbeat_due = self.last_heartbeat_sent + self.heartbeat_interval
        now = self.engine.get_clock().now()
        if now >= next_heartbeat_due:
            self._send_heartbeat()
            self.last_heartbeat_sent = now
        #
        # Outbound documents
        if self.q_outbound_documents:
            doc = self.q_outbound_documents.popleft()
            b_complete = 1
            #
            # message_type(1) + b_complete(1) + overhead for the vs (2) => 4
            docpart_overhead = 4
            max_fulldoc_size = self.max_packet_size - docpart_overhead
            if len(doc) > max_fulldoc_size:
                ret = doc[max_fulldoc_size:]
                self.q_outbound_documents.appendleft(ret)
                doc = doc[:max_fulldoc_size]
                b_complete = 0
            #
            payload = self.gruel_press.create_docdata_payload(
                b_complete=b_complete,
                data=doc)
            self.engine.send(
                sid=self.client_sid,
                payload=payload)
    def send_document(self, doc):
        self.q_outbound_documents.append(doc)
    #
    def get_status(self):
        '''
        Returns helpful messages that lets its parent class understand
        what state it is in.
        '''
        return self.status.name
    def order_connect(self, addr, port, password, cb_connect, cb_condrop, cb_doc):
        '''
        The reason for the callbacks is because the class that this is
        emcapsulated within will probably want to log that activity.
        Moreover, if there is a connection abort, they may wish to take
        corrective action.
        '''
        if None != self.client_sid:
            log('order_connect: Already connected. Early return.')
            return
        self.cb_connect = cb_connect
        self.cb_condrop = cb_condrop
        self.cb_doc = cb_doc
        self.doc_accumulator = []
        self._set_login_credentials(
            password=password)
        self.engine.open_tcp_client(
            addr=addr,
            port=port,
            cb_tcp_connect=self._engine_on_tcp_connect,
            cb_tcp_condrop=self._engine_on_tcp_condrop,
            cb_tcp_recv=self._engine_on_tcp_recv)
        self.status = ClientStatus.attempting_tcp_connection
    def order_condrop(self):
        if None == self.client_sid:
            log('order_condrop: Not connected. Early return.')
            return
        self.engine.close_tcp_client(
            sid=self.client_sid)
        self.status = ClientStatus.dormant
    #
    def _engine_on_tcp_connect(self, cs_tcp_connect):
        engine = cs_tcp_connect.engine
        client_sid = cs_tcp_connect.client_sid
        addr = cs_tcp_connect.addr
        port = cs_tcp_connect.port
        #
        self.client_sid = client_sid
        self.cb_connect()
        self.status = ClientStatus.ready_to_attempt_login
        self.last_heartbeat_recv = engine.get_clock().now()
        self.last_heartbeat_sent = engine.get_clock().now()
    def _engine_on_tcp_condrop(self, cs_tcp_condrop):
        engine = cs_tcp_condrop.engine
        client_sid = cs_tcp_condrop.client_sid
        message = cs_tcp_condrop.message
        #
        self.cb_condrop(message)
        self.status = ClientStatus.dormant
        self.client_sid = None
    def _engine_on_tcp_recv(self, cs_tcp_recv):
        engine = cs_tcp_recv.engine
        client_sid = cs_tcp_recv.client_sid
        data = cs_tcp_recv.data
        #
        d_message = self.gruel_puff.unpack(
            payload=data)
        gmt = gmt_value_to_name(d_message['message_type'])
        if gmt == 'client_login':
            hexdump_bytes(data)
            raise Exception("Client should not receive client_login")
        elif gmt == 'server_greet':
            self.status = ClientStatus.streaming
            mps = d_message['max_packet_size']
            if mps != None:
                self.max_packet_size = mps
        elif gmt == 'heartbeat':
            # this is us receiving a heartbeat from the server. so, we
            # send a heartbeat back
            self.last_heartbeat_recv = self.engine.get_clock().now()
        elif gmt == 'docdata':
            data = d_message['data']
            b_complete = d_message['b_complete']
            #
            log('received %s %s [%s]'%(len(data), b_complete, data)) # xxx
            #
            self.doc_accumulator.append(data)
            if b_complete == 1:
                doc = ''.join(self.doc_accumulator)
                self.doc_accumulator = []
                self.cb_doc(
                    doc=doc)
        else:
            hexdump_bytes(data)
            raise Exception("Unhandled message type %s"%gmt)
    #
    def _set_login_credentials(self, password):
        self.login_credentials.password = password
    def _attempt_login(self):
        payload = self.gruel_press.create_client_login_payload(
            password=self.login_credentials.password,
            heartbeat_interval=self.heartbeat_interval)
        self.engine.send(
            sid=self.client_sid,
            payload=payload)
        self.status = ClientStatus.login_message_in_flight
    def _send_heartbeat(self):
        payload = self.gruel_press.create_heartbeat_payload()
        self.engine.send(
            sid=self.client_sid,
            payload=payload)

def spin_gruel_client_new(engine, gruel_press, gruel_puff):
    ob = SpinGruelClient(
        engine=engine,
        gruel_press=gruel_press,
        gruel_puff=gruel_puff)
    return ob

