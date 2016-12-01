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

from solent.eng import activity_new
from solent.eng import gruel_schema_new
from solent.eng import gruel_press_new
from solent.eng import gruel_puff_new
from solent.eng import nearcast_orb_new
from solent.eng import nearcast_schema_new
from solent.eng.cs import *
from solent.eng.gruel.gruel_schema import GruelMessageType
from solent.eng.gruel.prop_gruel_server import I_NEARCAST_GRUEL_SERVER
from solent.eng.gruel.server.tcp_server_cog import tcp_server_cog_new
from solent.log import log
from solent.util import uniq

from testing import run_tests
from testing import test
from testing.eng import engine_fake

import sys

MTU = 500

def create_sid():
    return 'fake_sid_%s'%(uniq())

class ReceiverCog:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.nearnote = []
        self.suspect_client_message = []
    #
    def on_nearnote(self, s):
        self.nearnote.append(s)
    def count_nearnote(self):
        return len(self.nearnote)
    def get_nearnote(self):
        return self.nearnote
    def last_nearnote(self):
        return self.nearnote[-1]
    def log_nearnote(self):
        for l in self.nearnote:
            log(l)
    #
    def on_suspect_client_message(self, d_gruel):
        log('on_suspect_client_message')
        self.suspect_client_message.append(d_gruel)
    def count_suspect_client_message(self):
        return len(self.suspect_client_message)
    def last_suspect_client_message(self):
        return self.suspect_client_message[-1]

def start_service(orb, addr, port, username, password):
    orb.nearcast(
        cog_h='testing',
        message_h='start_service',
        addr=addr,
        port=port,
        username=username,
        password=password)
    orb.cycle()

def send_all_ips_are_valid(orb):
    orb.nearcast(
        cog_h='testing',
        message_h='all_ips_are_valid')
    orb.cycle()

def stop_service(orb):
    orb.nearcast(
        cog_h='testing',
        message_h='stop_service')
    orb.cycle()

def send_valid_ip(orb, ip):
    orb.nearcast(
        cog_h='testing',
        message_h='valid_ip',
        ip=ip)
    orb.cycle()

def simulate_client_connect(engine, orb, tcp_server_cog, ip, port):
    cs_tcp_connect = CsTcpConnect()
    cs_tcp_connect.engine = engine
    cs_tcp_connect.client_sid = create_sid()
    cs_tcp_connect.addr = ip
    cs_tcp_connect.port = port
    tcp_server_cog._engine_on_tcp_connect(
        cs_tcp_connect=cs_tcp_connect)
    orb.cycle()

def simulate_client_condrop(engine, orb, tcp_server_cog):
    cs_tcp_condrop = CsTcpCondrop()
    cs_tcp_condrop.engine = engine
    cs_tcp_condrop.client_sid = create_sid()
    cs_tcp_condrop.message = 'testing'
    tcp_server_cog._engine_on_tcp_condrop(
        cs_tcp_condrop=cs_tcp_condrop)
    orb.cycle()

def simulate_client_send_login(engine, orb, tcp_server_cog, uname, pw, hbint):
    gruel_schema = gruel_schema_new()
    gruel_press = gruel_press_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    gruel_puff = gruel_puff_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    #
    payload = gruel_press.create_client_login_payload(
        username=uname,
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
    nearcast_schema = nearcast_schema_new(
        i_nearcast=I_NEARCAST_GRUEL_SERVER)
    orb = nearcast_orb_new(
        engine=engine,
        nearcast_schema=nearcast_schema)
    #
    r = ReceiverCog(
        cog_h='receiver_cog',
        orb=orb,
        engine=engine)
    tcp_server_cog = tcp_server_cog_new(
        cog_h='tcp_server_cog',
        orb=orb,
        engine=engine)
    #
    orb.add_cog(r)
    orb.add_cog(tcp_server_cog)
    #
    addr = '127.0.0.1'
    port = 5000
    username = 'aaa'
    password = 'bbb'
    #
    # confirm starting state
    orb.cycle()
    assert 0 == r.count_nearnote()
    assert tcp_server_cog.server_sid == None
    assert tcp_server_cog.client_sid == None
    #
    # scenario: start the server
    start_service(
        orb=orb,
        addr=addr,
        port=port,
        username=username,
        password=password)
    #
    # confirm effects
    assert r.count_nearnote() == 1
    assert r.last_nearnote() == 'tcp_server_cog: listening'
    assert tcp_server_cog.server_sid != None
    assert tcp_server_cog.client_sid == None
    #
    # scenario: stop the service
    stop_service(
        orb=orb)
    #
    # confirm effects
    assert r.count_nearnote() == 2
    assert r.last_nearnote() == 'tcp_server_cog: stopped'
    assert tcp_server_cog.server_sid == None
    assert tcp_server_cog.client_sid == None
    #
    return True

@test
def should_handle_client_connect_and_then_boot_client():
    engine = engine_fake()
    nearcast_schema = nearcast_schema_new(
        i_nearcast=I_NEARCAST_GRUEL_SERVER)
    orb = nearcast_orb_new(
        engine=engine,
        nearcast_schema=nearcast_schema)
    #
    r = ReceiverCog(
        cog_h='receiver_cog',
        orb=orb,
        engine=engine)
    tcp_server_cog = tcp_server_cog_new(
        cog_h='tcp_server_cog',
        orb=orb,
        engine=engine)
    #
    orb.add_cog(r)
    orb.add_cog(tcp_server_cog)
    #
    addr = '127.0.0.1'
    port = 5000
    username = 'aaa'
    password = 'bbb'
    #
    # confirm starting state
    orb.cycle()
    assert 0 == r.count_nearnote()
    assert tcp_server_cog.server_sid == None
    assert tcp_server_cog.client_sid == None
    #
    # scenario: start the server
    start_service(
        orb=orb,
        addr=addr,
        port=port,
        username=username,
        password=password)
    orb.cycle()
    #
    # confirm effects
    assert r.count_nearnote() == 1
    assert r.last_nearnote() == 'tcp_server_cog: listening'
    assert tcp_server_cog.server_sid != None
    assert tcp_server_cog.client_sid == None
    #
    # scenario: client connects from tcp-invald ip address
    inv_ip = '203.15.93.2'
    inv_port = 1234
    simulate_client_connect(
        engine=engine,
        orb=orb,
        tcp_server_cog=tcp_server_cog,
        ip=inv_ip,
        port=inv_port)
    #
    # confirm effects
    assert r.last_nearnote() == 'tcp_server_cog: invalid_ip/%s:%s'%(inv_ip, inv_port)
    assert tcp_server_cog.server_sid != None
    assert tcp_server_cog.client_sid == None
    #
    # scenario: permission an ip, then client connects from valid ip address
    addr_to_permit = '203.15.93.150'
    port_to_permit = 6000
    send_valid_ip(
        orb=orb,
        ip=addr_to_permit)
    simulate_client_connect(
        engine=engine,
        orb=orb,
        tcp_server_cog=tcp_server_cog,
        ip=addr_to_permit,
        port=port_to_permit)
    #
    # confirm effects
    assert r.last_nearnote() == 'tcp_server_cog: client_connect/%s:%s'%(addr_to_permit, port_to_permit)
    assert tcp_server_cog.server_sid == None
    assert tcp_server_cog.client_sid != None
    #
    # scenario: stop the service, booting the client in the process
    stop_service(
        orb=orb)
    #
    # confirm effects
    assert r.get_nearnote()[-2] == 'tcp_server_cog: booting_client'
    assert r.last_nearnote() == 'tcp_server_cog: stopped'
    assert tcp_server_cog.server_sid == None
    assert tcp_server_cog.client_sid == None
    #
    return True

@test
def should_broadcast_incoming_message_as_suspect():
    engine = engine_fake()
    nearcast_schema = nearcast_schema_new(
        i_nearcast=I_NEARCAST_GRUEL_SERVER)
    orb = nearcast_orb_new(
        engine=engine,
        nearcast_schema=nearcast_schema)
    #
    r = ReceiverCog(
        cog_h='receiver_cog',
        orb=orb,
        engine=engine)
    tcp_server_cog = tcp_server_cog_new(
        cog_h='tcp_server_cog',
        orb=orb,
        engine=engine)
    #
    orb.add_cog(r)
    orb.add_cog(tcp_server_cog)
    #
    addr = '127.0.0.1'
    port = 5000
    username = 'aaa'
    password = 'bbb'
    #
    # get to a point where the client is logged in
    start_service(
        orb=orb,
        addr=addr,
        port=port,
        username=username,
        password=password)
    send_all_ips_are_valid(
        orb=orb)
    simulate_client_connect(
        engine=engine,
        orb=orb,
        tcp_server_cog=tcp_server_cog,
        ip=addr,
        port=port)
    #
    # confirm starting position
    assert r.last_nearnote() == 'tcp_server_cog: client_connect/%s:%s'%(
        addr, port)
    assert tcp_server_cog.server_sid == None
    assert tcp_server_cog.client_sid != None
    #
    # scenario: client sends a message
    client_send_username = 'ccc'
    client_send_password = 'ddd'
    client_send_hbint = 3
    simulate_client_send_login(
        engine=engine,
        orb=orb,
        tcp_server_cog=tcp_server_cog,
        uname=client_send_username,
        pw=client_send_password,
        hbint=client_send_hbint)
    #
    # confirm effects
    assert 1 == r.count_suspect_client_message()
    d_gruel = r.last_suspect_client_message()
    assert d_gruel['message_h'] == 'client_login'
    assert d_gruel['heartbeat_interval'] == client_send_hbint
    assert d_gruel['username'] == client_send_username
    assert d_gruel['password'] == client_send_password
    #
    # scenario: client disconnect
    simulate_client_condrop(
        engine=engine,
        orb=orb,
        tcp_server_cog=tcp_server_cog)
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

'''
@test
def should_send_heartbeat_when_told_to
'''

if __name__ == '__main__':
    run_tests(
        unders_file=sys.modules['__main__'].__file__)

