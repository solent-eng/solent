#
# prop_gruel_client
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

from testing import run_tests
from testing import test
from testing.eng import engine_fake
from testing.util import clock_fake

from solent.eng import activity_new
from solent.eng import cs
from solent.eng import gruel_puff_new
from solent.eng import gruel_press_new
from solent.eng import gruel_schema_new
from solent.eng import prop_gruel_client_new
from solent.log import hexdump_bytearray
from solent.util import uniq

import sys

class ConnectionInfo:
    def __init__(self):
        self.calls_to_on_connect = 0
        self.calls_to_on_condrop = 0
    def on_connect(self, cs_tcp_connect):
        self.calls_to_on_connect += 1
    def on_condrop(self, cs_tcp_condrop):
        self.calls_to_on_condrop += 1

MTU = 1492

@test
def should_start_at_dormant_status():
    engine = engine_fake()
    gruel_schema = gruel_schema_new()
    gruel_press = gruel_press_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    gruel_puff = gruel_puff_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    prop_gruel_client = prop_gruel_client_new(
        engine=engine,
        gruel_press=gruel_press,
        gruel_puff=gruel_puff)
    #
    # confirm status
    assert prop_gruel_client.get_status() == 'dormant'
    #
    return True

@test
def should_attempt_connection():
    addr = '127.0.0.1'
    port = 4098
    #
    engine = engine_fake()
    gruel_schema = gruel_schema_new()
    gruel_press = gruel_press_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    gruel_puff = gruel_puff_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    prop_gruel_client = prop_gruel_client_new(
        engine=engine,
        gruel_press=gruel_press,
        gruel_puff=gruel_puff)
    #
    connection_info = ConnectionInfo()
    #
    # connection attempt
    assert 0 == len(engine.events)
    prop_gruel_client.attempt_connection(
        addr=addr,
        port=port,
        username='uname',
        password='pword',
        cb_connect=connection_info.on_connect,
        cb_condrop=connection_info.on_condrop)
    #
    # confirm effects
    assert 0 == connection_info.calls_to_on_condrop
    assert 0 == connection_info.calls_to_on_connect
    assert 1 == len(engine.events)
    assert engine.events[-1] == ('open_tcp_client', addr, port)
    assert prop_gruel_client.get_status() == 'attempting_tcp_connection'
    #
    return True

@test
def should_return_to_dormant_on_failed_connection():
    addr = '127.0.0.1'
    port = 4098
    #
    engine = engine_fake()
    gruel_schema = gruel_schema_new()
    gruel_press = gruel_press_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    gruel_puff = gruel_puff_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    prop_gruel_client = prop_gruel_client_new(
        engine=engine,
        gruel_press=gruel_press,
        gruel_puff=gruel_puff)
    #
    connection_info = ConnectionInfo()
    #
    # connection attempt
    assert 0 == len(engine.events)
    prop_gruel_client.attempt_connection(
        addr=addr,
        port=port,
        username='uname',
        password='pword',
        cb_connect=connection_info.on_connect,
        cb_condrop=connection_info.on_condrop)
    #
    # confirm effects
    assert prop_gruel_client.get_status() == 'attempting_tcp_connection'
    #
    # simulate the engine rejecting the connection
    cs_tcp_condrop = cs.CsTcpCondrop()
    cs_tcp_condrop.engine = engine
    cs_tcp_condrop.sid = uniq()
    cs_tcp_condrop.message = 'test123'
    prop_gruel_client._engine_on_tcp_condrop(
        cs_tcp_condrop=cs_tcp_condrop)
    #
    # confirm effects
    assert 0 == connection_info.calls_to_on_connect
    assert 1 == connection_info.calls_to_on_condrop
    assert prop_gruel_client.get_status() == 'dormant'
    #
    return True

@test
def should_handle_successful_tcp_connection():
    addr = '127.0.0.1'
    port = 4098
    #
    engine = engine_fake()
    gruel_schema = gruel_schema_new()
    gruel_press = gruel_press_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    gruel_puff = gruel_puff_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    prop_gruel_client = prop_gruel_client_new(
        engine=engine,
        gruel_press=gruel_press,
        gruel_puff=gruel_puff)
    #
    connection_info = ConnectionInfo()
    #
    # connection attempt
    assert 0 == len(engine.events)
    prop_gruel_client.attempt_connection(
        addr=addr,
        port=port,
        username='uname',
        password='pword',
        cb_connect=connection_info.on_connect,
        cb_condrop=connection_info.on_condrop)
    #
    # have engine indicate connection success
    cs_tcp_connect = cs.CsTcpConnect()
    cs_tcp_connect.engine = engine
    cs_tcp_connect.sid = uniq()
    cs_tcp_connect.message = 'test123'
    prop_gruel_client._engine_on_tcp_connect(
        cs_tcp_connect=cs_tcp_connect)
    #
    # confirm effects
    assert 1 == connection_info.calls_to_on_connect
    assert 0 == connection_info.calls_to_on_condrop
    assert prop_gruel_client.get_status() == 'ready_to_attempt_login'
    #
    return True

@test
def should_attempt_login_and_receive_login_success():
    MAX_PACKET_LEN = 800
    #
    # get our engine going
    engine = engine_fake()
    clock = engine.get_clock()
    #
    gruel_schema = gruel_schema_new()
    gruel_press = gruel_press_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    gruel_puff = gruel_puff_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    prop_gruel_client = prop_gruel_client_new(
        engine=engine,
        gruel_press=gruel_press,
        gruel_puff=gruel_puff)
    assert prop_gruel_client.heartbeat_interval == 1
    #
    # other bits we'll need
    activity = activity_new()
    connection_info = ConnectionInfo()
    #
    # scenario: connection attempt
    assert 0 == len(engine.events)
    addr = '127.0.0.1'
    port = 4098
    username = 'uname'
    password = 'pword'
    prop_gruel_client.attempt_connection(
        addr=addr,
        port=port,
        username=username,
        password=password,
        cb_connect=connection_info.on_connect,
        cb_condrop=connection_info.on_condrop)
    #
    # scenario: successful connection
    # (here we simulate the engine calling back to the client to say
    # that there connection was successful)
    clock.set(5)
    cs_tcp_connect = cs.CsTcpConnect()
    cs_tcp_connect.engine = engine
    cs_tcp_connect.sid = uniq()
    cs_tcp_connect.message = 'test123'
    prop_gruel_client._engine_on_tcp_connect(
        cs_tcp_connect=cs_tcp_connect)
    #
    # confirm effects
    assert prop_gruel_client.get_status() == 'ready_to_attempt_login'
    assert prop_gruel_client.last_heartbeat_recv == 5
    assert prop_gruel_client.last_heartbeat_sent == 5
    #
    # give the client a turn so it can move to logging in.
    prop_gruel_client.at_turn(
        activity=activity)
    #
    # confirm effects
    assert activity.get()[-1] == 'PropGruelClient/sending login'
    assert prop_gruel_client.get_status() == 'login_message_in_flight'
    #
    # do we see the login message in-flight?
    assert 1 == len(engine.sent_data)
    latest_payload = engine.sent_data[-1]
    d_client_login = gruel_puff.unpack(
        payload=latest_payload)
    assert d_client_login['message_h'] == 'client_login'
    assert d_client_login['username'] == username
    assert d_client_login['password'] == password
    assert d_client_login['heartbeat_interval'] == 1
    #
    # simulate server sending back a successful login. (first, we create
    # the kind of payload that the server would have created in this
    # circumstance. Then we call back to the client in the same way that
    # a real engine would call back to it.)
    def server_sends_greet_payload():
        server_greet_payload = gruel_press.create_server_greet_payload(
            max_packet_len=MAX_PACKET_LEN)
        cs_tcp_recv = cs.CsTcpRecv()
        cs_tcp_recv.engine = engine
        cs_tcp_recv.client_sid = 'fake_sid'
        cs_tcp_recv.data = server_greet_payload
        prop_gruel_client._engine_on_tcp_recv(
            cs_tcp_recv=cs_tcp_recv)
    server_sends_greet_payload()
    #
    # confirm effects
    assert prop_gruel_client.get_status() == 'streaming'
    #
    # scenario: server sends a heartbeat
    clock.set(10)
    def server_sends_heartbeat():
        server_heartbeat = gruel_press.create_heartbeat_payload()
        cs_tcp_recv = cs.CsTcpRecv()
        cs_tcp_recv.engine = engine
        cs_tcp_recv.client_sid = 'fake_sid'
        cs_tcp_recv.data = server_heartbeat
        prop_gruel_client._engine_on_tcp_recv(
            cs_tcp_recv=cs_tcp_recv)
    server_sends_heartbeat()
    #
    # confirm effects
    assert prop_gruel_client.get_status() == 'streaming'
    assert prop_gruel_client.last_heartbeat_recv == 10
    #
    # scenario: client should send a heartbeat
    clock.set(11)
    prop_gruel_client.at_turn(
        activity=activity)
    #
    # confirm effects
    assert 2 == len(engine.sent_data)
    payload = engine.sent_data[-1]
    d_payload = gruel_puff.unpack(
        payload=payload)
    assert d_payload['message_h'] == 'heartbeat'
    #
    # confirm that it now does not send another one
    prop_gruel_client.at_turn(
        activity=activity)
    assert 2 == len(engine.sent_data)
    #
    # scenario: client sends a small payload
    small_doc = '''
        i greet message
        greet "hello, world!"
    '''
    mcount_before = len(engine.sent_data)
    prop_gruel_client.send_document(
        doc=small_doc)
    prop_gruel_client.at_turn(
        activity=activity)
    #
    # confirm effects
    assert len(engine.sent_data) == (mcount_before + 1)
    payload = engine.sent_data[-1]
    d_payload = gruel_puff.unpack(
        payload=payload)
    assert d_payload['message_h'] == 'docdata'
    assert d_payload['b_complete'] == 1
    assert d_payload['data'] == small_doc
    #
    # scenario: client sends a payload that must span several
    # packets
    large_doc = 'w%sy'%('x'*(2*MAX_PACKET_LEN))
    mcount_before = len(engine.sent_data)
    prop_gruel_client.send_document(
        doc=large_doc)
    # give it several turns to allow doc to be dispatched
    prop_gruel_client.at_turn(activity)
    prop_gruel_client.at_turn(activity)
    prop_gruel_client.at_turn(activity)
    #
    # confirm effects
    assert len(engine.sent_data) > mcount_before
    #   (inspect first packet)
    d_payload = gruel_puff.unpack(
        payload=engine.sent_data[mcount_before])
    assert d_payload['message_h'] == 'docdata'
    assert d_payload['b_complete'] == 0
    assert d_payload['data'][0] == 'w'
    #   (inspect next-to-last packet)
    d_payload = gruel_puff.unpack(
        payload=engine.sent_data[-2])
    assert d_payload['message_h'] == 'docdata'
    assert d_payload['b_complete'] == 0
    assert d_payload['data'][-1] == 'x'
    #   (inspect last packet)
    d_payload = gruel_puff.unpack(
        payload=engine.sent_data[-1])
    assert d_payload['message_h'] == 'docdata'
    assert d_payload['b_complete'] == 1
    assert d_payload['data'][-1] == 'y'
    #
    # scenario: client receives a single-packet payload
    #
    # confirm effects
    #
    # scenario: client receives a multi-packet payload that requires
    # buffering
    #
    # confirm effects
    #
    return True

if __name__ == '__main__':
    run_tests(
        unders_file=sys.modules['__main__'].__file__)

