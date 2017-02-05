#
# spin_gruel_client (testing)
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

from fake.util import fake_clock_new

from testing import run_tests
from testing import test

from solent import uniq
from solent.eng import activity_new
from solent.eng import cs
from solent.eng import engine_new
from solent.gruel import gruel_puff_new
from solent.gruel import gruel_press_new
from solent.gruel import gruel_protocol_new
from solent.gruel import spin_gruel_client_new
from solent.log import hexdump_bytes
from solent.log import log

from collections import deque
import sys
import time

# having this small makes debugging easier
MTU = 120

class ConnectionInfo:
    def __init__(self):
        self.calls_to_on_connect = 0
        self.calls_to_on_condrop = 0
    def on_connect(self):
        self.calls_to_on_connect += 1
    def on_condrop(self, message):
        self.calls_to_on_condrop += 1

class DocReceiver:
    def __init__(self):
        self.docs = []
    def on_doc(self, doc):
        self.docs.append(doc)

class SpinReneGruelServer:
    def __init__(self, spin_h, engine, gruel_protocol, gruel_press, gruel_puff):
        self.spin_h = spin_h
        self.engine = engine
        self.gruel_protocol = gruel_protocol
        self.gruel_press = gruel_press
        self.gruel_puff = gruel_puff
        #
        self.b_active = False
        self.ip = None
        self.port = None
        self.accept_sid = None
        self.server_sid = None
        self.received_message_ds = None
    def at_turn(self, activity):
        pass
    def at_close(self):
        self._close_everything()
    #
    def is_server_listening(self):
        return self.server_sid != None
    def is_accept_connected(self):
        return self.accept_sid != None
    def start(self, ip, port):
        self.ip = ip
        self.port = port
        #
        self.b_active = True
        self._start_server()
    def stop(self):
        self.b_active = False
        self._close_everything()
    def send_server_greet(self, max_packet_size):
        bb = self.gruel_press.create_server_greet_bb(
            max_packet_size=max_packet_size)
        self.engine.send(
            sid=self.accept_sid,
            bb=bb)
    def send_server_bye(self, notes):
        bb = self.gruel_press.create_server_bye_bb(
            notes=notes)
        self.engine.send(
            sid=self.accept_sid,
            bb=bb)
    def send_heartbeat(self):
        bb = self.gruel_press.create_heartbeat_bb()
        self.engine.send(
            sid=self.accept_sid,
            bb=bb)
    def send_docpart(self, b_complete, msg):
        bb = self.gruel_press.create_docdata_bb(
            b_complete=b_complete,
            data=msg)
        self.engine.send(
            sid=self.accept_sid,
            bb=bb)
    #
    def _close_everything(self):
        self.b_active = False
        self._boot_any_accept()
        self._boot_any_server()
    def _boot_any_accept(self):
        if self.accept_sid != None:
            self.engine.close_tcp_accept(
                accept_sid=self.accept_sid)
    def _boot_any_server(self):
        if self.server_sid != None:
            self.engine.close_tcp_server(
                server_sid=self.server_sid)
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
        self.server_sid = None
    def _engine_on_tcp_accept_connect(self, cs_tcp_accept_connect):
        engine = cs_tcp_accept_connect.engine
        server_sid = cs_tcp_accept_connect.server_sid
        accept_sid = cs_tcp_accept_connect.accept_sid
        client_addr = cs_tcp_accept_connect.client_addr
        client_port = cs_tcp_accept_connect.client_port
        #
        self.accept_sid = accept_sid
        self.received_message_ds = []
        self._stop_server()
    def _engine_on_tcp_accept_condrop(self, cs_tcp_accept_condrop):
        engine = cs_tcp_accept_condrop.engine
        server_sid = cs_tcp_accept_condrop.server_sid
        accept_sid = cs_tcp_accept_condrop.accept_sid
        #
        self.accept_sid = None
        self.received_message_ds = None
        if self.b_active:
            self._start_server()
    def _engine_on_tcp_accept_recv(self, cs_tcp_accept_recv):
        engine = cs_tcp_accept_recv.engine
        accept_sid = cs_tcp_accept_recv.accept_sid
        bb = cs_tcp_accept_recv.bb
        #
        hexdump_bytes(
            arr=bb,
            title='_engine_on_tcp_accept_recv')
        d_message = self.gruel_puff.unpack(
            bb=bb)
        self.received_message_ds.append(d_message)
    def _start_server(self):
        self.engine.open_tcp_server(
            addr=self.ip,
            port=self.port,
            cb_tcp_server_start=self._engine_on_tcp_server_start,
            cb_tcp_server_stop=self._engine_on_tcp_server_stop,
            cb_tcp_accept_connect=self._engine_on_tcp_accept_connect,
            cb_tcp_accept_condrop=self._engine_on_tcp_accept_condrop,
            cb_tcp_accept_recv=self._engine_on_tcp_accept_recv)
    def _stop_server(self):
        self.engine.close_tcp_server(
            server_sid=self.server_sid)

@test
def should_start_at_dormant_status():
    engine = engine_new(
        mtu=MTU)
    gruel_protocol = gruel_protocol_new()
    gruel_press = gruel_press_new(
        gruel_protocol=gruel_protocol,
        mtu=MTU)
    gruel_puff = gruel_puff_new(
        gruel_protocol=gruel_protocol,
        mtu=MTU)
    spin_gruel_client = engine.init_spin(
        construct=spin_gruel_client_new,
        gruel_press=gruel_press,
        gruel_puff=gruel_puff)
    #
    # confirm status
    engine.cycle()
    assert spin_gruel_client.get_status() == 'dormant'
    #
    return True

@test
def should_successfully_connect_and_log_in():
    addr = '127.0.0.1'
    port = 4098
    password = 'pass1234'
    #
    connection_info = ConnectionInfo()
    doc_receiver = DocReceiver()
    gruel_protocol = gruel_protocol_new()
    gruel_press = gruel_press_new(
        gruel_protocol=gruel_protocol,
        mtu=MTU)
    gruel_puff = gruel_puff_new(
        gruel_protocol=gruel_protocol,
        mtu=MTU)
    #
    engine = engine_new(
        mtu=MTU)
    #
    # step: start our fake gruel server
    server = engine.init_spin(
        construct=SpinReneGruelServer,
        gruel_protocol=gruel_protocol,
        gruel_press=gruel_press,
        gruel_puff=gruel_puff)
    server.start(
        ip=addr,
        port=port)
    #
    # verify
    engine.cycle()
    assert server.is_server_listening() == True
    assert server.is_accept_connected() == False
    #
    # step: spin_gruel_client connects to our rene server
    spin_gruel_client = engine.init_spin(
        construct=spin_gruel_client_new,
        gruel_press=gruel_press,
        gruel_puff=gruel_puff)
    spin_gruel_client.order_connect(
        addr=addr,
        port=port,
        password=password,
        cb_connect=connection_info.on_connect,
        cb_condrop=connection_info.on_condrop,
        cb_doc=doc_receiver.on_doc)
    #
    # verify
    engine.cycle()
    assert spin_gruel_client.get_status() == 'login_message_in_flight'
    assert server.is_server_listening() == False
    assert server.is_accept_connected() == True
    assert 0 == connection_info.calls_to_on_connect
    assert 0 == connection_info.calls_to_on_condrop
    #
    # step: server confirms login with a 'server_greet' message
    server.send_server_greet(
        max_packet_size=1000)
    #
    # confirm effects
    engine.cycle()
    assert spin_gruel_client.get_status() == 'streaming'
    #
    # cleanup
    server.stop()
    #
    return True

@test
def should_callback_and_go_dormant_on_failed_connection():
    addr = '127.0.0.1'
    port = 4098
    password = 'pass1234'
    #
    connection_info = ConnectionInfo()
    doc_receiver = DocReceiver()
    gruel_protocol = gruel_protocol_new()
    gruel_press = gruel_press_new(
        gruel_protocol=gruel_protocol,
        mtu=MTU)
    gruel_puff = gruel_puff_new(
        gruel_protocol=gruel_protocol,
        mtu=MTU)
    #
    engine = engine_new(
        mtu=MTU)
    #
    # step: spin_gruel_client connects to our non-existent rene server
    spin_gruel_client = engine.init_spin(
        construct=spin_gruel_client_new,
        gruel_press=gruel_press,
        gruel_puff=gruel_puff)
    spin_gruel_client.order_connect(
        addr=addr,
        port=port,
        password=password,
        cb_connect=connection_info.on_connect,
        cb_condrop=connection_info.on_condrop,
        cb_doc=doc_receiver.on_doc)
    #
    # verify
    engine.cycle()
    assert spin_gruel_client.get_status() == 'dormant'
    assert 0 == connection_info.calls_to_on_connect
    assert 1 == connection_info.calls_to_on_condrop
    #
    return True

@test
def should_callback_and_go_dormant_on_failed_login():
    addr = '127.0.0.1'
    port = 4098
    password = 'pass1234'
    #
    connection_info = ConnectionInfo()
    doc_receiver = DocReceiver()
    gruel_protocol = gruel_protocol_new()
    gruel_press = gruel_press_new(
        gruel_protocol=gruel_protocol,
        mtu=MTU)
    gruel_puff = gruel_puff_new(
        gruel_protocol=gruel_protocol,
        mtu=MTU)
    #
    engine = engine_new(
        mtu=MTU)
    #
    # step: start our fake gruel server
    server = engine.init_spin(
        construct=SpinReneGruelServer,
        gruel_protocol=gruel_protocol,
        gruel_press=gruel_press,
        gruel_puff=gruel_puff)
    server.start(
        ip=addr,
        port=port)
    #
    # verify
    engine.cycle()
    assert server.is_server_listening() == True
    assert server.is_accept_connected() == False
    #
    # step: spin_gruel_client connects to our rene server
    spin_gruel_client = engine.init_spin(
        construct=spin_gruel_client_new,
        gruel_press=gruel_press,
        gruel_puff=gruel_puff)
    spin_gruel_client.order_connect(
        addr=addr,
        port=port,
        password=password,
        cb_connect=connection_info.on_connect,
        cb_condrop=connection_info.on_condrop,
        cb_doc=doc_receiver.on_doc)
    #
    # verify
    engine.cycle()
    assert spin_gruel_client.get_status() == 'login_message_in_flight'
    assert server.is_server_listening() == False
    assert server.is_accept_connected() == True
    assert 0 == connection_info.calls_to_on_connect
    assert 0 == connection_info.calls_to_on_condrop
    #
    # step: server confirms login with a 'server_greet' message
    server.send_server_bye(
        notes='we are booting you')
    #
    # confirm effects
    engine.cycle()
    assert spin_gruel_client.get_status() == 'dormant'
    assert 0 == connection_info.calls_to_on_connect
    assert 1 == connection_info.calls_to_on_condrop
    #
    # cleanup
    server.stop()
    #
    return True

@test
def should_send_and_receive_heartbeats():
    addr = '127.0.0.1'
    port = 4098
    password = 'pass1234'
    #
    fake_clock = fake_clock_new()
    connection_info = ConnectionInfo()
    doc_receiver = DocReceiver()
    gruel_protocol = gruel_protocol_new()
    gruel_press = gruel_press_new(
        gruel_protocol=gruel_protocol,
        mtu=MTU)
    gruel_puff = gruel_puff_new(
        gruel_protocol=gruel_protocol,
        mtu=MTU)
    #
    engine = engine_new(
        mtu=MTU)
    engine.clock = fake_clock
    #
    # step: start our fake gruel server
    server = engine.init_spin(
        construct=SpinReneGruelServer,
        gruel_protocol=gruel_protocol,
        gruel_press=gruel_press,
        gruel_puff=gruel_puff)
    server.start(
        ip=addr,
        port=port)
    #
    # verify
    engine.cycle()
    assert server.is_server_listening() == True
    assert server.is_accept_connected() == False
    #
    # step: spin_gruel_client connects to our rene server
    spin_gruel_client = engine.init_spin(
        construct=spin_gruel_client_new,
        gruel_press=gruel_press,
        gruel_puff=gruel_puff)
    spin_gruel_client.order_connect(
        addr=addr,
        port=port,
        password=password,
        cb_connect=connection_info.on_connect,
        cb_condrop=connection_info.on_condrop,
        cb_doc=doc_receiver.on_doc)
    #
    # verify
    engine.cycle()
    assert spin_gruel_client.get_status() == 'login_message_in_flight'
    assert server.is_server_listening() == False
    assert server.is_accept_connected() == True
    assert 0 == connection_info.calls_to_on_connect
    assert 0 == connection_info.calls_to_on_condrop
    #
    # step: server confirms login with a 'server_greet' message
    server.send_server_greet(
        max_packet_size=1000)
    #
    # confirm effects
    engine.cycle()
    assert spin_gruel_client.get_status() == 'streaming'
    assert 1 == len(server.received_message_ds)
    #
    # step: move the clock forward towards a heartbeat
    fake_clock.inc(
        amt=spin_gruel_client.heartbeat_interval)
    t = fake_clock.now()
    #
    # verify that our rene server gets a heartbeat
    engine.cycle()
    assert 2 == len(server.received_message_ds)
    d_message = server.received_message_ds[-1]
    assert d_message['message_h'] == 'heartbeat'
    #
    # step: send a heartbeat from our rene server
    server.send_heartbeat()
    #
    # verify that our spin client hasn't crashed (that's all I'm worried
    # about at the moment
    engine.cycle()
    assert spin_gruel_client.last_heartbeat_recv == t
    #
    # cleanup
    server.stop()
    #
    return True

@test
def should_receive_payloads_correctly():
    addr = '127.0.0.1'
    port = 4098
    password = 'pass1234'
    #
    fake_clock = fake_clock_new()
    connection_info = ConnectionInfo()
    doc_receiver = DocReceiver()
    gruel_protocol = gruel_protocol_new()
    gruel_press = gruel_press_new(
        gruel_protocol=gruel_protocol,
        mtu=MTU)
    gruel_puff = gruel_puff_new(
        gruel_protocol=gruel_protocol,
        mtu=MTU)
    #
    engine = engine_new(
        mtu=MTU)
    engine.clock = fake_clock
    #
    # step: start our fake gruel server
    server = engine.init_spin(
        construct=SpinReneGruelServer,
        gruel_protocol=gruel_protocol,
        gruel_press=gruel_press,
        gruel_puff=gruel_puff)
    server.start(
        ip=addr,
        port=port)
    #
    # verify
    engine.cycle()
    assert server.is_server_listening() == True
    assert server.is_accept_connected() == False
    #
    # step: spin_gruel_client connects to our rene server
    spin_gruel_client = engine.init_spin(
        construct=spin_gruel_client_new,
        gruel_press=gruel_press,
        gruel_puff=gruel_puff)
    spin_gruel_client.order_connect(
        addr=addr,
        port=port,
        password=password,
        cb_connect=connection_info.on_connect,
        cb_condrop=connection_info.on_condrop,
        cb_doc=doc_receiver.on_doc)
    #
    # verify
    engine.cycle()
    assert spin_gruel_client.get_status() == 'login_message_in_flight'
    assert server.is_server_listening() == False
    assert server.is_accept_connected() == True
    assert 0 == connection_info.calls_to_on_connect
    assert 0 == connection_info.calls_to_on_condrop
    #
    # step: server confirms login with a 'server_greet' message
    server.send_server_greet(
        max_packet_size=1000)
    #
    # confirm effects
    engine.cycle()
    assert spin_gruel_client.get_status() == 'streaming'
    assert 1 == len(server.received_message_ds)
    #
    # step: server sends a single-part package
    msg = 'abcabc'
    server.send_docpart(
        b_complete=1,
        msg=msg)
    #
    # confirm effects
    engine.cycle()
    assert 1 == len(doc_receiver.docs)
    assert doc_receiver.docs[-1] == msg
    #
    # step: server sends a multi-part package
    msg = 'ddd'
    server.send_docpart(
        b_complete=0,
        msg=msg)
    msg = 'eee'
    server.send_docpart(
        b_complete=1,
        msg=msg)
    #
    # confirm effects
    engine.cycle()
    log('doc_receiver.docs %s'%str(doc_receiver.docs))
    assert 2 == len(doc_receiver.docs)
    assert doc_receiver.docs[-1] == 'dddeee'
    #
    return True

@test
def should_send_payloads_correctly():
    addr = '127.0.0.1'
    port = 4098
    password = 'pass1234'
    #
    fake_clock = fake_clock_new()
    connection_info = ConnectionInfo()
    doc_receiver = DocReceiver()
    gruel_protocol = gruel_protocol_new()
    gruel_press = gruel_press_new(
        gruel_protocol=gruel_protocol,
        mtu=MTU)
    gruel_puff = gruel_puff_new(
        gruel_protocol=gruel_protocol,
        mtu=MTU)
    #
    engine = engine_new(
        mtu=MTU)
    engine.enable_nodelay()
    engine.clock = fake_clock
    #
    # step: start our fake gruel server
    server = engine.init_spin(
        construct=SpinReneGruelServer,
        gruel_protocol=gruel_protocol,
        gruel_press=gruel_press,
        gruel_puff=gruel_puff)
    server.start(
        ip=addr,
        port=port)
    #
    # verify
    engine.cycle()
    assert server.is_server_listening() == True
    assert server.is_accept_connected() == False
    #
    # step: spin_gruel_client connects to our rene server
    spin_gruel_client = engine.init_spin(
        construct=spin_gruel_client_new,
        gruel_press=gruel_press,
        gruel_puff=gruel_puff)
    spin_gruel_client.order_connect(
        addr=addr,
        port=port,
        password=password,
        cb_connect=connection_info.on_connect,
        cb_condrop=connection_info.on_condrop,
        cb_doc=doc_receiver.on_doc)
    #
    # verify
    engine.cycle()
    assert spin_gruel_client.get_status() == 'login_message_in_flight'
    assert server.is_server_listening() == False
    assert server.is_accept_connected() == True
    assert 0 == connection_info.calls_to_on_connect
    assert 0 == connection_info.calls_to_on_condrop
    #
    # step: server confirms login with a 'server_greet' message
    max_packet_size = 100
    server.send_server_greet(
        max_packet_size=max_packet_size)
    #
    # confirm effects
    engine.cycle()
    assert spin_gruel_client.get_status() == 'streaming'
    assert 1 == len(server.received_message_ds)
    #
    # step: client sends a significant document
    large_doc = 'w/%s/y'%('x'*(2*max_packet_size))
    spin_gruel_client.send_document(
        doc=large_doc)
    #
    # confirm effects
    engine.cycle() # select can only see one packet here
    assert server.received_message_ds[-3]['data'][0] == 'w'
    assert server.received_message_ds[-3]['data'][-1] == 'x'
    assert server.received_message_ds[-2]['data'][0] == 'x'
    assert server.received_message_ds[-2]['data'][-1] == 'x'
    assert server.received_message_ds[-1]['data'][-1] == 'y'
    #
    return True

if __name__ == '__main__':
    run_tests(
        unders_file=sys.modules['__main__'].__file__)

