#
# prop_gruel_server (testing)
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
from solent.eng import prop_gruel_server_new
from solent.log import hexdump_bytearray
from solent.util import uniq

import sys

MTU = 1492

class ConnectionInfo:
    def __init__(self):
        self.calls_to_on_connect = 0
        self.calls_to_on_condrop = 0
    def on_tcp_connect(self, cs_tcp_connect):
        self.calls_to_on_connect += 1
    def on_tcp_condrop(self, cs_tcp_condrop):
        self.calls_to_on_condrop += 1

class DocReceiver:
    def __init__(self):
        self.docs = []
    def on_doc(self, doc):
        self.docs.append(doc)

def start_server(engine, prop_gruel_server, addr, port, username, password, connection_info, doc_receiver):
    prop_gruel_server.activate(
        addr=addr,
        port=port,
        username=username,
        password=password,
        cb_tcp_connect=connection_info.on_tcp_connect,
        cb_tcp_condrop=connection_info.on_tcp_condrop,
        cb_doc=doc_receiver.on_doc)
    # confirm effects
    assert prop_gruel_server.get_status() == 'listening'
    assert prop_gruel_server.server_sid != None
    assert prop_gruel_server.client_sid == None
    assert engine.events[-1] == ('open_tcp_server', addr, port)
    assert prop_gruel_server.server_username == username
    assert prop_gruel_server.server_password == password

def stop_server(engine, prop_gruel_server):
    prop_gruel_server.stop()
    #
    # confirm effects, particularly that client got booted
    assert prop_gruel_server.get_status() == 'stopped'
    assert prop_gruel_server.server_sid == None
    assert prop_gruel_server.client_sid == None

def simulate_client_connection(engine, prop_gruel_server, connection_info):
    calls_to_on_connect = connection_info.calls_to_on_connect
    #
    cs_tcp_connect = cs.CsTcpConnect()
    cs_tcp_connect.engine = engine
    cs_tcp_connect.client_sid = 'fake_client_sid_%s'%uniq()
    cs_tcp_connect.addr = '203.15.93.2'
    cs_tcp_connect.port = 1190
    prop_gruel_server._engine_on_tcp_connect(
        cs_tcp_connect=cs_tcp_connect)
    # confirm effects, particularly that the server blocks
    assert engine.events[-1] == ('close_tcp_server',)
    assert connection_info.calls_to_on_connect == calls_to_on_connect+1
    assert prop_gruel_server.get_status() == 'tcp_up_awaiting_login'
    assert prop_gruel_server.server_sid == None
    assert prop_gruel_server.client_sid != None

def simulate_client_disconnect(engine, prop_gruel_server, addr, port):
    cs_tcp_condrop = cs.CsTcpCondrop()
    cs_tcp_condrop.engine = engine
    cs_tcp_condrop.client_sid = 'fake_client_sid_%s'%uniq()
    cs_tcp_condrop.message = 'simulated_drop'
    prop_gruel_server._engine_on_tcp_condrop(
        cs_tcp_condrop=cs_tcp_condrop)
    # confirm effects, particularly the server restarting
    assert prop_gruel_server.get_status() == 'listening'
    assert prop_gruel_server.server_sid != None
    assert prop_gruel_server.client_sid == None
    assert engine.events[-1] == ('open_tcp_server', addr, port)

def sim_client_logon(engine, prop_gruel_server, gruel_press, uname, pw):
    payload = gruel_press.create_client_login_payload(
        username=uname,
        password=pw,
        heartbeat_interval=1)
    #
    cs_tcp_recv = cs.CsTcpRecv()
    cs_tcp_recv.engine = engine
    cs_tcp_recv.client_sid = 'fake_sid_%s'%uniq()
    cs_tcp_recv.data = payload
    #
    prop_gruel_server._engine_on_tcp_recv(
        cs_tcp_recv=cs_tcp_recv)

@test
def should_construct_to_dormant_status():
    engine = engine_fake()
    gruel_schema = gruel_schema_new()
    gruel_press = gruel_press_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    gruel_puff = gruel_puff_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    prop_gruel_server = prop_gruel_server_new(
        engine=engine,
        gruel_press=gruel_press,
        gruel_puff=gruel_puff)
    #
    # confirm effects
    assert prop_gruel_server.get_status() == 'stopped'
    #
    return True

@test
def should_start_and_stop_tcp_listener():
    engine = engine_fake()
    gruel_schema = gruel_schema_new()
    gruel_press = gruel_press_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    gruel_puff = gruel_puff_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    prop_gruel_server = prop_gruel_server_new(
        engine=engine,
        gruel_press=gruel_press,
        gruel_puff=gruel_puff)
    #
    connection_info = ConnectionInfo()
    doc_receiver = DocReceiver()
    addr = '127.0.0.1'
    port = 6420
    username = 'asdf_testguy'
    password = 'poiuy'
    #
    # scenario: server starts
    start_server(
        engine=engine,
        prop_gruel_server=prop_gruel_server,
        addr=addr,
        port=port,
        username=username,
        password=password,
        connection_info=connection_info,
        doc_receiver=doc_receiver)
    #
    # scenario: simple server stop
    stop_server(
        engine=engine,
        prop_gruel_server=prop_gruel_server)
    #
    # confirm effects: server should have been stopped
    assert engine.events[-1] == ('close_tcp_server',)
    #
    # scenario: server starts, client connects, then we stop server
    start_server(
        engine=engine,
        prop_gruel_server=prop_gruel_server,
        addr=addr,
        port=port,
        username=username,
        password=password,
        connection_info=connection_info,
        doc_receiver=doc_receiver)
    simulate_client_connection(
        engine=engine,
        prop_gruel_server=prop_gruel_server,
        connection_info=connection_info)
    stop_server(
        engine=engine,
        prop_gruel_server=prop_gruel_server)
    #
    # confirm effects: client should have been booted
    assert engine.events[-1] == ('close_tcp_client',)
    #
    # scenario: we start the server, client connects, client disconnects, we
    # stop the server
    start_server(
        engine=engine,
        prop_gruel_server=prop_gruel_server,
        addr=addr,
        port=port,
        username=username,
        password=password,
        connection_info=connection_info,
        doc_receiver=doc_receiver)
    simulate_client_connection(
        engine=engine,
        prop_gruel_server=prop_gruel_server,
        connection_info=connection_info)
    simulate_client_disconnect(
        engine=engine,
        prop_gruel_server=prop_gruel_server,
        addr=addr,
        port=port)
    stop_server(
        engine=engine,
        prop_gruel_server=prop_gruel_server)
    assert engine.events[-1] == ('close_tcp_server',)
    #
    return True

@test
def should_boot_clients_with_bad_credentials():
    activity = activity_new()
    engine = engine_fake()
    gruel_schema = gruel_schema_new()
    gruel_press = gruel_press_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    gruel_puff = gruel_puff_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    prop_gruel_server = prop_gruel_server_new(
        engine=engine,
        gruel_press=gruel_press,
        gruel_puff=gruel_puff)
    #
    connection_info = ConnectionInfo()
    doc_receiver = DocReceiver()
    addr = '127.0.0.1'
    port = 6420
    username = 'asdf_testguy'
    password = 'poiuy'
    #
    # scenario: server starts, client connects
    event_len = len(engine.events)
    start_server(
        engine=engine,
        prop_gruel_server=prop_gruel_server,
        addr=addr,
        port=port,
        username=username,
        password=password,
        connection_info=connection_info,
        doc_receiver=doc_receiver)
    simulate_client_connection(
        engine=engine,
        prop_gruel_server=prop_gruel_server,
        connection_info=connection_info)
    sim_client_logon(
        engine=engine,
        prop_gruel_server=prop_gruel_server,
        gruel_press=gruel_press,
        uname='bad_username',
        pw='password')
    prop_gruel_server.at_turn(
        activity=activity)
    print(engine.events[-1])
    #
    assert len(engine.events) == event_len
    #
    # now adjust clock
    engine.clock.add(5)
    prop_gruel_server.at_turn(
        activity=activity)
    #
    # confirm effects: server should have been stopped
    assert len(engine.events) == event_len + 2
    assert engine.events[-2] == ('close_tcp_client',)
    assert engine.events[-1] == ('open_tcp_server', addr, port)

@test
def should_boot_clients_who_send_data_packets_without_being_logging_in():
    engine = engine_fake()
    gruel_schema = gruel_schema_new()
    gruel_press = gruel_press_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    gruel_puff = gruel_puff_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    prop_gruel_server = prop_gruel_server_new(
        engine=engine,
        gruel_press=gruel_press,
        gruel_puff=gruel_puff)
    #
    connection_info = ConnectionInfo()
    doc_receiver = DocReceiver()
    addr = '127.0.0.1'
    port = 6420
    username = 'asdf_testguy'
    password = 'poiuy'
    start_server(
        engine=engine,
        prop_gruel_server=prop_gruel_server,
        addr=addr,
        port=port,
        username=username,
        password=password,
        connection_info=connection_info,
        doc_receiver=doc_receiver)
    simulate_client_connection(
        engine=engine,
        prop_gruel_server=prop_gruel_server,
        connection_info=connection_info)
    def simulate_receiving_bad_login_username_message():
        payload = gruel_press.create_client_login_payload(
            username='deliberately_invalid',
            password=password,
            heartbeat_interval=1)
        cs_tcp_recv = cs.CsTcpRecv()
        cs_tcp_recv.engine = engine
        cs_tcp_recv.client_sid = 'fake_client_sid_%s'%uniq()
        cs_tcp_recv.data = payload
        prop_gruel_server._engine_on_tcp_recv(
            cs_tcp_recv=cs_tcp_recv)
        #
        # confirm effects: server sends bye, boots client, returns to
        # listening
    simulate_receiving_bad_login_username_message()

"""
@test
def should_accept_good_login():
    pass

@test
def should_deny_bad_login():
    engine = engine_fake()
    gruel_schema = gruel_schema_new()
    gruel_press = gruel_press_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    gruel_puff = gruel_puff_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    prop_gruel_server = prop_gruel_server_new(
        engine=engine,
        gruel_press=gruel_press,
        gruel_puff=gruel_puff)
    #
    connection_info = ConnectionInfo()
    doc_receiver = DocReceiver()
    addr = '127.0.0.1'
    port = 6420
    start_server(
        engine=engine,
        prop_gruel_server=prop_gruel_server,
        addr=addr,
        port=port,
        username=username,
        password=password,
        connection_info=connection_info,
        doc_receiver=doc_receiver)
    simulate_client_connection(
        engine=engine,
        prop_gruel_server=prop_gruel_server,
        connection_info=connection_info)
    def simulate_receiving_bad_login_message():
"""
        
"""
@test
def should_reset_not_logged_in_status_after_disconnect():
    pass
"""

"""
@test
def should_send_payloads_to_client():
    engine = engine_fake()
    gruel_schema = gruel_schema_new()
    gruel_press = gruel_press_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    gruel_puff = gruel_puff_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    prop_gruel_server = prop_gruel_server_new(
        engine=engine,
        gruel_press=gruel_press,
        gruel_puff=gruel_puff)
    #
    connection_info = ConnectionInfo()
    doc_receiver = DocReceiver()
    #
    # preparation: get the server going
    addr = '127.0.0.1'
    port = 6420
    start_server(
        engine=engine,
        prop_gruel_server=prop_gruel_server,
        addr=addr,
        port=port,
        username=username,
        password=password,
        connection_info=connection_info,
        doc_receiver=doc_receiver)
    simulate_client_connection(
        engine=engine,
        prop_gruel_server=prop_gruel_server,
        connection_info=connection_info)
    #
    # scenario: send a small document towards the client
    small_doc = '''
        i paint_type h drying_rate
        paint_type acrylic 1
        paint_type oil 5
        paint_type watercolour 14
    '''
    #xxx
    #
    # confirm effects
    #xxx
    #
    # scenario: send a large document towards the client
    #xxx
    #
    # confirm effects
    #xxx
    #
"""

"""
@test
def should_send_and_receive_heartbeats():

"""

if __name__ == '__main__':
    run_tests(
        unders_file=sys.modules['__main__'].__file__)

