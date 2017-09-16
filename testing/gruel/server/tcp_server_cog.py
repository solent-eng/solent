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

from solent import uniq
from solent.eng import activity_new
from solent import Engine
from solent.gruel import gruel_protocol_new
from solent.gruel import gruel_press_new
from solent.gruel import gruel_puff_new
from solent.gruel.gruel_protocol import GruelMessageType
from solent.gruel.server.nearcast import I_NEARCAST_GRUEL_SERVER
from solent.gruel.server.tcp_server_cog import tcp_server_cog_new
from solent import log
from solent.test import run_tests
from solent.test import test

import sys

MTU = 500


# --------------------------------------------------------
#   :rene
# --------------------------------------------------------
#
# This is a manufactured client that behaves on the wire like a real
# client. But it's much simpler: we're able to poke it in the test
# cases to do exactly the behaviour we want.
#
class SpinReneClient:
    """
    Named after Decartes, reference to brain in a vat. This client does what
    we tell it to to prompt the server, making it brain-in-a-vat-like.
    """
    def __init__(self, spin_h, engine):
        self.spin_h = spin_h
        self.engine = engine
        #
        self.gruel_protocol = None
        self.gruel_press = None
        self.gruel_puff = None
        #
        self.ip = None
        self.port = None
        self.client_sid = None
        self.b_have_received_something = None
        self.sb_recv = None
    def eng_turn(self, activity):
        pass
    def eng_close(self):
        pass
    #
    def _engine_on_tcp_client_connect(self, cs_tcp_client_connect):
        engine = cs_tcp_client_connect.engine
        client_sid = cs_tcp_client_connect.client_sid
        addr = cs_tcp_client_connect.addr
        port = cs_tcp_client_connect.port
        #
        log('rene connect')
        self.client_sid = client_sid
        self.sb_recv = []
        self.b_have_received_something = False
    def _engine_on_tcp_client_condrop(self, cs_tcp_client_condrop):
        engine = cs_tcp_client_condrop.engine
        client_sid = cs_tcp_client_condrop.client_sid
        message = cs_tcp_client_condrop.message
        #
        log('rene condrop')
        self.client_sid = None
        self.sb_recv = None
    def _engine_on_tcp_client_recv(self, cs_tcp_client_recv):
        engine = cs_tcp_client_recv.engine
        client_sid = cs_tcp_client_recv.client_sid
        bb = cs_tcp_client_recv.bb
        #
        self.sb_recv.append(bb)
        self.b_have_received_something = True
    def _start_server(self):
        self.engine.open_tcp_client(
            addr=self.ip,
            port=self.port,
            cb_tcp_client_connect=self._engine_on_tcp_client_connect,
            cb_tcp_client_condrop=self._engine_on_tcp_client_condrop,
            cb_tcp_client_recv=self._engine_on_tcp_client_recv)
    def _stop_server(self):
        self.engine.close_tcp_client(
            client_sid=self.client_sid)
    #
    def init(self):
        self.gruel_protocol = gruel_protocol_new()
        self.gruel_press = gruel_press_new(
            gruel_protocol=self.gruel_protocol,
            mtu=MTU)
        self.gruel_puff = gruel_puff_new(
            gruel_protocol=self.gruel_protocol,
            mtu=MTU)
    def start(self, ip, port):
        self.ip = ip
        self.port = port
        self._start_server()
    def send_invalid_gruel(self):
        bb = bytes('this string is invalid gruel', 'utf8')
        self.engine.send(
            sid=self.client_sid,
            bb=bb)
    def send_login(self, pw, hbint):
        bb = self.gruel_press.create_client_login_bb(
            password=pw,
            heartbeat_interval=hbint)
        self.engine.send(
            sid=self.client_sid,
            bb=bb)
    def disconnect(self):
        self._stop_server()

def spin_rene_client_new(spin_h, engine):
    ob = SpinReneClient(
        spin_h=spin_h,
        engine=engine)
    return ob


# --------------------------------------------------------
#   :old_rest
# --------------------------------------------------------
class FakeCog:
    def __init__(self):
        self.cog_h = 'testing'

def create_sid():
    return 'fake_sid_%s'%(uniq())


# --------------------------------------------------------
#   rest
# --------------------------------------------------------
@test
def should_start_and_stop():
    engine = Engine(
        mtu=MTU)
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST_GRUEL_SERVER)
    bridge = orb.init_testbridge()
    tcp_server_cog = orb.init_cog(
        construct=tcp_server_cog_new)
    #
    addr = '127.0.0.1'
    port = 5000
    password = 'bbb'
    #
    # confirm starting state
    orb.cycle()
    assert False == tcp_server_cog.is_server_listening()
    assert False == tcp_server_cog.is_accept_connected()
    #
    # scenario: start the server
    bridge.nc_start_service(
        ip=addr,
        port=port,
        password=password)
    #
    # confirm effects
    orb.cycle()
    assert True == tcp_server_cog.is_server_listening()
    assert False == tcp_server_cog.is_accept_connected()
    #
    # scenario: stop the service
    bridge.nc_stop_service()
    #
    # confirm effects
    orb.cycle()
    assert False == tcp_server_cog.is_server_listening()
    assert False == tcp_server_cog.is_accept_connected()
    #
    return True

@test
def should_handle_client_connect_and_then_boot_client():
    engine = Engine(
        mtu=MTU)
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST_GRUEL_SERVER)
    bridge = orb.init_testbridge()
    tcp_server_cog = orb.init_cog(
        construct=tcp_server_cog_new)
    #
    addr = '127.0.0.1'
    port = 5000
    password = 'bbb'
    #
    # confirm starting state
    assert 0 == bridge.count_announce_tcp_connect()
    assert False == tcp_server_cog.is_server_listening()
    assert False == tcp_server_cog.is_accept_connected()
    #
    # scenario: start the server
    bridge.nc_start_service(
        ip=addr,
        port=port,
        password=password)
    #
    # confirm effects
    assert 0 == bridge.count_announce_tcp_connect()
    assert True == tcp_server_cog.is_server_listening()
    assert False == tcp_server_cog.is_accept_connected()
    #
    # scenario: client connects
    rene = engine.init_spin(
        construct=spin_rene_client_new)
    rene.init()
    rene.start(
        ip=addr,
        port=port)
    #
    # confirm effects
    engine.cycle()
    assert 1 == bridge.count_announce_tcp_connect()
    assert False == tcp_server_cog.is_server_listening()
    assert True == tcp_server_cog.is_accept_connected()
    #
    # scenario: stop the service, booting the client in the process
    bridge.nc_stop_service()
    #
    # confirm effects
    assert False == tcp_server_cog.is_server_listening()
    assert False == tcp_server_cog.is_accept_connected()
    #
    return True

@test
def should_broadcast_incoming_message_as_gruel_in():
    engine = Engine(
        mtu=MTU)
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST_GRUEL_SERVER)
    #
    bridge = orb.init_testbridge()
    tcp_server_cog = orb.init_cog(
        construct=tcp_server_cog_new)
    #
    addr = '127.0.0.1'
    port = 5000
    password = 'bbb'
    #
    # get to a point where the client is logged in
    bridge.nc_start_service(
        ip=addr,
        port=port,
        password=password)
    rene = engine.init_spin(
        construct=spin_rene_client_new)
    rene.init()
    rene.start(
        ip=addr,
        port=port)
    #
    # confirm starting position
    engine.cycle()
    assert 1 == bridge.count_announce_tcp_connect()
    assert False == tcp_server_cog.is_server_listening()
    assert True == tcp_server_cog.is_accept_connected()
    #
    # scenario: client sends a message
    client_send_password = 'ddd'
    client_send_hbint = 3
    rene.send_login(
        pw=client_send_password,
        hbint=client_send_hbint)
    #
    # confirm effects
    engine.cycle()
    assert 1 == bridge.count_gruel_recv()
    d_gruel = bridge.last_gruel_recv()[0]
    assert d_gruel['message_h'] == 'client_login'
    assert d_gruel['heartbeat_interval'] == client_send_hbint
    assert d_gruel['password'] == client_send_password
    #
    # scenario: client disconnect
    rene.disconnect()
    #
    # confirm effects
    engine.cycle()
    assert True == tcp_server_cog.is_server_listening()
    assert False == tcp_server_cog.is_accept_connected()
    #
    # scenario: close server
    bridge.nc_stop_service()
    #
    # confirm effects
    engine.cycle()
    assert False == tcp_server_cog.is_server_listening()
    assert False == tcp_server_cog.is_accept_connected()
    #
    return True

@test
def should_boot_client_when_told_to():
    engine = Engine(
        mtu=MTU)
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST_GRUEL_SERVER)
    #
    bridge = orb.init_testbridge()
    tcp_server_cog = orb.init_cog(
        construct=tcp_server_cog_new)
    #
    addr = '127.0.0.1'
    port = 5000
    password = 'bbb'
    #
    # get to a point where the client is logged in
    bridge.nc_start_service(
        ip=addr,
        port=port,
        password=password)
    rene = engine.init_spin(
        construct=spin_rene_client_new)
    rene.init()
    rene.start(
        ip=addr,
        port=port)
    #
    # confirm starting position
    engine.cycle()
    assert 1 == bridge.count_announce_tcp_connect()
    assert False == tcp_server_cog.is_server_listening()
    assert True == tcp_server_cog.is_accept_connected()
    #
    # scenario: we receive a boot message
    bridge.nc_please_tcp_boot()
    #
    # check effects: we want to see that the connection has been dropped and
    # that the server is back up
    engine.cycle()
    assert True == tcp_server_cog.is_server_listening()
    assert False == tcp_server_cog.is_accept_connected()
    #
    # cleanup
    bridge.nc_stop_service()
    engine.cycle()
    #
    return True

@test
def should_boot_client_when_invalid_gruel_is_received():
    activity = activity_new()
    engine = Engine(
        mtu=MTU)
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST_GRUEL_SERVER)
    #
    bridge = orb.init_testbridge()
    tcp_server_cog = orb.init_cog(
        construct=tcp_server_cog_new)
    engine.cycle()
    #
    addr = '127.0.0.1'
    port = 5000
    password = 'bbb'
    #
    # get to a point where the client is logged in
    bridge.nc_start_service(
        ip=addr,
        port=port,
        password=password)
    engine.cycle()
    rene = engine.init_spin(
        construct=spin_rene_client_new)
    rene.init()
    rene.start(
        ip=addr,
        port=port)
    #
    # confirm starting position
    engine.cycle()
    assert 1 == bridge.count_announce_tcp_connect()
    assert 0 == bridge.count_please_tcp_boot()
    assert False == tcp_server_cog.is_server_listening()
    assert True == tcp_server_cog.is_accept_connected()
    #
    # scenario: send invalid data as though it is gruel
    rene.send_invalid_gruel()
    #
    # confirm effects: nearcast a boot message
    engine.cycle()
    assert 1 == bridge.count_please_tcp_boot()
    assert True == tcp_server_cog.is_server_listening()
    assert False == tcp_server_cog.is_accept_connected()
    #
    # cleanup
    bridge.nc_stop_service()
    engine.cycle()
    #
    return True

@test
def should_ignore_gruel_send_when_no_client():
    gruel_protocol = gruel_protocol_new()
    gruel_press = gruel_press_new(
        gruel_protocol=gruel_protocol,
        mtu=MTU)
    gruel_puff = gruel_puff_new(
        gruel_protocol=gruel_protocol,
        mtu=MTU)
    #
    engine = Engine(
        mtu=MTU)
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST_GRUEL_SERVER)
    bridge = orb.init_testbridge()
    tcp_server_cog = orb.init_cog(
        construct=tcp_server_cog_new)
    #
    addr = '127.0.0.1'
    port = 5000
    password = 'bbb'
    #
    # confirm starting state
    engine.cycle()
    assert 0 == bridge.count_announce_tcp_connect()
    assert False == tcp_server_cog.is_server_listening()
    assert False == tcp_server_cog.is_accept_connected()
    #
    # scenario: start the server
    bridge.nc_start_service(
        ip=addr,
        port=port,
        password=password)
    #
    # confirm effects
    engine.cycle()
    assert 0 == bridge.count_announce_tcp_connect()
    assert True == tcp_server_cog.is_server_listening()
    assert False == tcp_server_cog.is_accept_connected()
    #
    # scenario: tcp_server_cog gets gruel_send but client is not connected
    bridge.nc_gruel_send(
        bb=gruel_press.create_client_login_bb(
            password='8_password',
            heartbeat_interval=4))
    #
    # confirm effects: client should still be connected, and we should have
    # sent no packets to the engine.
    engine.cycle()
    assert True == tcp_server_cog.is_server_listening()
    assert False == tcp_server_cog.is_accept_connected()
    #
    # now the client connects. they should get nothing.
    rene = engine.init_spin(
        construct=spin_rene_client_new)
    rene.init()
    rene.start(
        ip=addr,
        port=port)
    #
    # verify
    engine.cycle()
    assert False == tcp_server_cog.is_server_listening()
    assert True == tcp_server_cog.is_accept_connected()
    assert False == rene.b_have_received_something
    #
    # cleanup
    bridge.nc_stop_service()
    engine.cycle()
    #
    return True

@test
def should_send_gruel_send_data_to_a_connected_client():
    '''
    In contrast to the last test, when a client /is/ connected, they
    should receive gruel data.
    '''
    gruel_protocol = gruel_protocol_new()
    gruel_press = gruel_press_new(
        gruel_protocol=gruel_protocol,
        mtu=MTU)
    gruel_puff = gruel_puff_new(
        gruel_protocol=gruel_protocol,
        mtu=MTU)
    #
    engine = Engine(
        mtu=MTU)
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST_GRUEL_SERVER)
    bridge = orb.init_testbridge()
    tcp_server_cog = orb.init_cog(
        construct=tcp_server_cog_new)
    #
    addr = '127.0.0.1'
    port = 5000
    password = 'bbb'
    #
    # confirm starting state
    assert 0 == bridge.count_announce_tcp_connect()
    assert False == tcp_server_cog.is_server_listening()
    assert False == tcp_server_cog.is_accept_connected()
    #
    # scenario: start the server
    bridge.nc_start_service(
        ip=addr,
        port=port,
        password=password)
    #
    # confirm effects
    assert 0 == bridge.count_announce_tcp_connect()
    assert True == tcp_server_cog.is_server_listening()
    assert False == tcp_server_cog.is_accept_connected()
    #
    # scenario: client connects
    rene = engine.init_spin(
        construct=spin_rene_client_new)
    rene.init()
    rene.start(
        ip=addr,
        port=port)
    #
    # confirm baseline
    engine.cycle()
    assert 1 == bridge.count_announce_tcp_connect()
    assert tcp_server_cog.is_accept_connected()
    #
    # scenario: tcp_server_cog gets gruel_send but client is not connected
    bridge.nc_gruel_send(
        bb=gruel_press.create_client_login_bb(
            password='8_password',
            heartbeat_interval=4))
    #
    # confirm effects: client should still be connected, and we should have
    # sent no packets to the engine.
    engine.cycle()
    assert tcp_server_cog.is_accept_connected()
    assert rene.b_have_received_something == True
    #
    # cleanup
    bridge.nc_stop_service()
    engine.cycle()
    #
    return True

if __name__ == '__main__':
    run_tests()

