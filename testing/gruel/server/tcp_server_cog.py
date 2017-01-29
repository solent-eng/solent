#
# tcp_server_cog (testing)
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
from testing.gruel.server.receiver_cog import receiver_cog_fake

from solent.eng import activity_new
from solent.eng.cs import *
from solent.gruel import gruel_schema_new
from solent.gruel import gruel_press_new
from solent.gruel import gruel_puff_new
from solent.gruel.gruel_schema import GruelMessageType
from solent.gruel.server.i_nearcast import I_NEARCAST_GRUEL_SERVER
from solent.gruel.server.tcp_server_cog import tcp_server_cog_new
from solent.log import log
from solent.util import uniq

import sys

MTU = 500

class FakeCog:
    def __init__(self):
        self.cog_h = 'testing'

def create_sid():
    return 'fake_sid_%s'%(uniq())

def start_service(orb, ip, port, password):
    orb.nearcast(
        cog=FakeCog(),
        message_h='start_service',
        ip=ip,
        port=port,
        password=password)
    orb.cycle()

def stop_service(orb):
    orb.nearcast(
        cog=FakeCog(),
        message_h='stop_service')
    orb.cycle()

def send_announce_tcp_connect(orb, ip, port):
    orb.nearcast(
        cog=FakeCog(),
        message_h='announce_tcp_connect',
        ip=ip,
        port=port)
    orb.cycle()

def simulate_client_connect(engine, orb, server_sid, ip, port):
    engine.simulate_tcp_client_connect(
        server_sid=server_sid,
        client_ip=ip,
        client_port=port)
    orb.cycle()

def simulate_client_condrop(engine, orb, tcp_server_cog):
    cs_tcp_condrop = CsTcpCondrop()
    cs_tcp_condrop.engine = engine
    cs_tcp_condrop.client_sid = create_sid()
    cs_tcp_condrop.message = 'testing'
    tcp_server_cog._engine_on_tcp_condrop(
        cs_tcp_condrop=cs_tcp_condrop)
    orb.cycle()

def simulate_client_send_login(engine, orb, tcp_server_cog, pw, hbint):
    gruel_schema = gruel_schema_new()
    gruel_press = gruel_press_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    gruel_puff = gruel_puff_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    #
    payload = gruel_press.create_client_login_payload(
        password=pw,
        heartbeat_interval=hbint)
    cs_tcp_recv = CsTcpRecv()
    cs_tcp_recv.engine = engine
    cs_tcp_recv.client_sid = create_sid()
    cs_tcp_recv.data = payload
    tcp_server_cog._engine_on_tcp_recv(
        cs_tcp_recv=cs_tcp_recv)
    orb.cycle()

@test
def should_start_and_stop():
    engine = engine_fake()
    orb = engine.init_orb(
        orb_h='app',
        i_nearcast=I_NEARCAST_GRUEL_SERVER)
    r = orb.init_cog(
        construct=receiver_cog_fake)
    tcp_server_cog = orb.init_cog(
        construct=tcp_server_cog_new)
    #
    addr = '127.0.0.1'
    port = 5000
    password = 'bbb'
    #
    # confirm starting state
    orb.cycle()
    assert tcp_server_cog.server_sid == None
    assert tcp_server_cog.client_sid == None
    #
    # scenario: start the server
    r.nc_start_service(
        ip=addr,
        port=port,
        password=password)
    #
    # confirm effects
    assert tcp_server_cog.server_sid != None
    assert tcp_server_cog.client_sid == None
    #
    # scenario: stop the service
    stop_service(
        orb=orb)
    #
    # confirm effects
    assert tcp_server_cog.server_sid == None
    assert tcp_server_cog.client_sid == None
    #
    return True

@test
def should_handle_client_connect_and_then_boot_client():
    engine = engine_fake()
    orb = engine.init_orb(
        orb_h='app',
        i_nearcast=I_NEARCAST_GRUEL_SERVER)
    r = orb.init_cog(
        construct=receiver_cog_fake)
    tcp_server_cog = orb.init_cog(
        construct=tcp_server_cog_new)
    #
    addr = '127.0.0.1'
    port = 5000
    password = 'bbb'
    #
    # confirm starting state
    assert 0 == r.count_announce_tcp_connect()
    assert tcp_server_cog.server_sid == None
    assert tcp_server_cog.client_sid == None
    #
    # scenario: start the server
    start_service(
        orb=orb,
        ip=addr,
        port=port,
        password=password)
    #
    # confirm effects
    assert 0 == r.count_announce_tcp_connect()
    assert tcp_server_cog.server_sid != None
    assert tcp_server_cog.client_sid == None
    #
    # scenario: client connects
    client_addr = '203.15.93.150'
    client_port = 6000
    simulate_client_connect(
        engine=engine,
        orb=orb,
        server_sid=tcp_server_cog.server_sid,
        ip=client_addr,
        port=client_port)
    #
    # confirm effects
    assert 1 == r.count_announce_tcp_connect()
    assert tcp_server_cog.server_sid == None
    assert tcp_server_cog.client_sid != None
    #
    # scenario: stop the service, booting the client in the process
    stop_service(
        orb=orb)
    #
    # confirm effects
    assert tcp_server_cog.server_sid == None
    assert tcp_server_cog.client_sid == None
    #
    return True

@test
def should_broadcast_incoming_message_as_gruel_in():
    engine = engine_fake()
    orb = engine.init_orb(
        orb_h='app',
        i_nearcast=I_NEARCAST_GRUEL_SERVER)
    #
    r = orb.init_cog(
        construct=receiver_cog_fake)
    tcp_server_cog = orb.init_cog(
        construct=tcp_server_cog_new)
    #
    addr = '127.0.0.1'
    port = 5000
    password = 'bbb'
    #
    # get to a point where the client is logged in
    start_service(
        orb=orb,
        ip=addr,
        port=port,
        password=password)
    simulate_client_connect(
        engine=engine,
        orb=orb,
        server_sid=tcp_server_cog.server_sid,
        ip='123.216.321.5',
        port=123)
    #
    # confirm starting position
    assert 1 == r.count_announce_tcp_connect()
    assert tcp_server_cog.server_sid == None
    assert tcp_server_cog.client_sid != None
    #
    # scenario: client sends a message
    client_send_password = 'ddd'
    client_send_hbint = 3
    simulate_client_send_login(
        engine=engine,
        orb=orb,
        tcp_server_cog=tcp_server_cog,
        pw=client_send_password,
        hbint=client_send_hbint)
    #
    # confirm effects
    assert 1 == r.count_gruel_recv()
    d_gruel = r.last_gruel_recv()
    assert d_gruel['message_h'] == 'client_login'
    assert d_gruel['heartbeat_interval'] == client_send_hbint
    assert d_gruel['password'] == client_send_password
    #
    # scenario: client disconnect
    simulate_client_condrop(
        engine=engine,
        orb=orb,
        tcp_server_cog=tcp_server_cog)
    orb.cycle()
    #
    # confirm effects
    assert tcp_server_cog.server_sid != None
    assert tcp_server_cog.client_sid == None
    #
    # scenario: close server
    stop_service(
        orb=orb)
    #
    # confirm effects
    assert tcp_server_cog.server_sid == None
    assert tcp_server_cog.client_sid == None
    #
    return True

@test
def should_boot_client_when_told_to():
    engine = engine_fake()
    orb = engine.init_orb(
        orb_h='app',
        i_nearcast=I_NEARCAST_GRUEL_SERVER)
    #
    r = orb.init_cog(
        construct=receiver_cog_fake)
    tcp_server_cog = orb.init_cog(
        construct=tcp_server_cog_new)
    #
    addr = '127.0.0.1'
    port = 5000
    password = 'bbb'
    #
    # get to a point where the client is logged in
    start_service(
        orb=orb,
        ip=addr,
        port=port,
        password=password)
    simulate_client_connect(
        engine=engine,
        orb=orb,
        server_sid=tcp_server_cog.server_sid,
        ip='205.231.231.123',
        port=2000)
    #
    # confirm starting position
    assert 1 == r.count_announce_tcp_connect()
    assert tcp_server_cog.server_sid == None
    assert tcp_server_cog.client_sid != None
    #
    # scenario: we receive a boot message
    r.nc_please_tcp_boot()
    #
    # check effects: we want to see that the connection has been dropped and
    # that the server is back up
    assert tcp_server_cog.server_sid != None
    assert tcp_server_cog.client_sid == None
    #
    return True

@test
def should_boot_client_when_invalid_gruel_is_received():
    activity = activity_new()
    engine = engine_fake()
    orb = engine.init_orb(
        orb_h='app',
        i_nearcast=I_NEARCAST_GRUEL_SERVER)
    #
    r = orb.init_cog(
        construct=receiver_cog_fake)
    tcp_server_cog = orb.init_cog(
        construct=tcp_server_cog_new)
    #
    addr = '127.0.0.1'
    port = 5000
    password = 'bbb'
    #
    # get to a point where the client is logged in
    start_service(
        orb=orb,
        ip=addr,
        port=port,
        password=password)
    simulate_client_connect(
        engine=engine,
        orb=orb,
        server_sid=tcp_server_cog.server_sid,
        ip='205.231.231.123',
        port=2000)
    #
    # confirm starting position
    assert 1 == r.count_announce_tcp_connect()
    assert 0 == r.count_please_tcp_boot()
    assert tcp_server_cog.server_sid == None
    assert tcp_server_cog.client_sid != None
    #
    # scenario: send invalid data as though it is gruel
    cs_tcp_recv = CsTcpRecv()
    cs_tcp_recv.engine = engine
    cs_tcp_recv.client_sid = create_sid()
    cs_tcp_recv.data = bytes('this string is invalid gruel', 'utf8')
    tcp_server_cog._engine_on_tcp_recv(
        cs_tcp_recv=cs_tcp_recv)
    orb.cycle()
    #
    # confirm effects: nearcast a boot message
    assert 1 == r.count_please_tcp_boot()
    assert tcp_server_cog.server_sid != None
    assert tcp_server_cog.client_sid == None
    #
    return True

@test
def should_ignore_gruel_send_when_no_client():
    gruel_schema = gruel_schema_new()
    gruel_press = gruel_press_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    gruel_puff = gruel_puff_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    #
    engine = engine_fake()
    orb = engine.init_orb(
        orb_h='app',
        i_nearcast=I_NEARCAST_GRUEL_SERVER)
    r = orb.init_cog(
        construct=receiver_cog_fake)
    tcp_server_cog = orb.init_cog(
        construct=tcp_server_cog_new)
    #
    addr = '127.0.0.1'
    port = 5000
    password = 'bbb'
    #
    # confirm starting state
    assert 0 == r.count_announce_tcp_connect()
    assert tcp_server_cog.server_sid == None
    assert tcp_server_cog.client_sid == None
    #
    # scenario: start the server
    start_service(
        orb=orb,
        ip=addr,
        port=port,
        password=password)
    #
    # confirm effects
    assert 0 == r.count_announce_tcp_connect()
    assert tcp_server_cog.server_sid != None
    assert tcp_server_cog.client_sid == None
    #
    # scenario: tcp_server_cog gets gruel_send but client is not connected
    r.nc_gruel_send(
        payload=gruel_press.create_client_login_payload(
            password='8_password',
            heartbeat_interval=4))
    orb.cycle()
    #
    # confirm effects: client should still be connected, and we should have
    # sent no packets to the engine.
    assert tcp_server_cog.server_sid != None
    assert tcp_server_cog.client_sid == None
    assert 0 == len(engine.sent_data)
    #
    return True

@test
def should_send_gruel_send_data_to_a_connected_client():
    gruel_schema = gruel_schema_new()
    gruel_press = gruel_press_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    gruel_puff = gruel_puff_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    #
    engine = engine_fake()
    orb = engine.init_orb(
        orb_h='app',
        i_nearcast=I_NEARCAST_GRUEL_SERVER)
    r = orb.init_cog(
        construct=receiver_cog_fake)
    tcp_server_cog = orb.init_cog(
        construct=tcp_server_cog_new)
    #
    addr = '127.0.0.1'
    port = 5000
    password = 'bbb'
    #
    # confirm starting state
    assert 0 == r.count_announce_tcp_connect()
    assert tcp_server_cog.server_sid == None
    assert tcp_server_cog.client_sid == None
    #
    # scenario: start the server
    start_service(
        orb=orb,
        ip=addr,
        port=port,
        password=password)
    #
    # confirm effects
    assert 0 == r.count_announce_tcp_connect()
    assert tcp_server_cog.server_sid != None
    assert tcp_server_cog.client_sid == None
    #
    # scenario: client connects
    client_addr = '203.15.93.150'
    client_port = 6000
    simulate_client_connect(
        engine=engine,
        orb=orb,
        server_sid=tcp_server_cog.server_sid,
        ip='205.231.231.123',
        port=2000)
    #
    # confirm baseline
    assert 1 == r.count_announce_tcp_connect()
    assert tcp_server_cog.server_sid == None
    assert tcp_server_cog.client_sid != None
    #
    # scenario: tcp_server_cog gets gruel_send but client is not connected
    r.nc_gruel_send(
        payload=gruel_press.create_client_login_payload(
            password='8_password',
            heartbeat_interval=4))
    orb.cycle()
    #
    # confirm effects: client should still be connected, and we should have
    # sent no packets to the engine.
    assert tcp_server_cog.server_sid == None
    assert tcp_server_cog.client_sid != None
    assert 1 == len(engine.sent_data)
    #
    return True

if __name__ == '__main__':
    run_tests(
        unders_file=sys.modules['__main__'].__file__)

