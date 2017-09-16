#
# server_customs_cog (testing)
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

from fake.eng import fake_engine_new

from testing.gruel.server.receiver_cog import receiver_cog_fake

from solent import uniq
from solent.eng import activity_new
from solent.eng.cs import *
from solent.gruel import gruel_protocol_new
from solent.gruel import gruel_press_new
from solent.gruel import gruel_puff_new
from solent.gruel.server.nearcast import I_NEARCAST_GRUEL_SERVER
from solent.gruel.server.server_customs_cog import server_customs_cog_new
from solent.gruel.server.server_customs_cog import ServerCustomsState
from solent import log
from solent.test import run_tests
from solent.test import test

from enum import Enum
import sys

MTU = 500

@test
def should_throw_alg_exception_if_packet_seen_before_password():
    engine = fake_engine_new()
    gruel_protocol = gruel_protocol_new()
    gruel_press = gruel_press_new(
        gruel_protocol=gruel_protocol,
        mtu=engine.mtu)
    gruel_puff = gruel_puff_new(
        gruel_protocol=gruel_protocol,
        mtu=engine.mtu)
    #
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST_GRUEL_SERVER)
    server_customs_cog = orb.init_cog(
        construct=server_customs_cog_new)
    r = orb.init_cog(
        construct=receiver_cog_fake)
    #
    # scenario: gruel_recv happens without a password having been set
    b_error = False
    try:
        r.nc_gruel_recv(
            d_gruel=gruel_puff.unpack(
                bb=gruel_press.create_heartbeat_bb()))
    except:
        b_error = True
    if b_error:
        return True
    else:
        log('expected an exception, did not get one')
        return False

@test
def should_store_password_values():
    engine = fake_engine_new()
    gruel_protocol = gruel_protocol_new()
    gruel_press = gruel_press_new(
        gruel_protocol=gruel_protocol,
        mtu=engine.mtu)
    gruel_puff = gruel_puff_new(
        gruel_protocol=gruel_protocol,
        mtu=engine.mtu)
    #
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST_GRUEL_SERVER)
    server_customs_cog = orb.init_cog(
        construct=server_customs_cog_new)
    r = orb.init_cog(
        construct=receiver_cog_fake)
    #
    # scenario: password message
    our_password = 'qweqwe'
    r.nc_start_service(
        ip='does not matter',
        port=1234,
        password=our_password)
    #
    # confirm effects
    assert server_customs_cog.expected_password == our_password
    #
    return True

@test
def should_boot_client_if_first_message_is_not_client_login():
    engine = fake_engine_new()
    clock = engine.get_clock()
    gruel_protocol = gruel_protocol_new()
    gruel_press = gruel_press_new(
        gruel_protocol=gruel_protocol,
        mtu=engine.mtu)
    gruel_puff = gruel_puff_new(
        gruel_protocol=gruel_protocol,
        mtu=engine.mtu)
    #
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST_GRUEL_SERVER)
    server_customs_cog = orb.init_cog(
        construct=server_customs_cog_new)
    r = orb.init_cog(
        construct=receiver_cog_fake)
    #
    # start the service
    our_password = 'qweqwe'
    r.nc_start_service(
        ip='does not matter',
        port=1234,
        password=our_password)
    #
    # check starting position
    assert 0 == r.count_please_tcp_boot()
    #
    # scenario: first message is not client_login
    r.nc_gruel_recv(
        d_gruel=gruel_puff.unpack(
            bb=gruel_press.create_heartbeat_bb()))
    orb.cycle()
    #
    # check effects
    assert server_customs_cog.expected_password == our_password
    #
    return True

@test
def should_boot_user_on_receipt_of_login_message_when_already_logged_in():
    engine = fake_engine_new()
    clock = engine.get_clock()
    gruel_protocol = gruel_protocol_new()
    gruel_press = gruel_press_new(
        gruel_protocol=gruel_protocol,
        mtu=engine.mtu)
    gruel_puff = gruel_puff_new(
        gruel_protocol=gruel_protocol,
        mtu=engine.mtu)
    #
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST_GRUEL_SERVER)
    server_customs_cog = orb.init_cog(
        construct=server_customs_cog_new)
    r = orb.init_cog(
        construct=receiver_cog_fake)
    #
    # start the service
    our_password = 'qweqwe'
    r.nc_start_service(
        ip='does not matter',
        port=1234,
        password=our_password)
    #
    # hack the starting position
    server_customs_cog.state = ServerCustomsState.authorised
    #
    # scenario: send a message that is client_login
    r.nc_gruel_recv(
        d_gruel=gruel_puff.unpack(
            bb=gruel_press.create_client_login_bb(
                password=our_password,
                heartbeat_interval=3)))
    orb.cycle()
    #
    # check effects
    assert server_customs_cog.state == ServerCustomsState.reject_stage_a
    #
    return True

@test
def should_do_basic_login_reject():
    engine = fake_engine_new()
    clock = engine.get_clock()
    gruel_protocol = gruel_protocol_new()
    gruel_press = gruel_press_new(
        gruel_protocol=gruel_protocol,
        mtu=engine.mtu)
    gruel_puff = gruel_puff_new(
        gruel_protocol=gruel_protocol,
        mtu=engine.mtu)
    #
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST_GRUEL_SERVER)
    server_customs_cog = orb.init_cog(
        construct=server_customs_cog_new)
    r = orb.init_cog(
        construct=receiver_cog_fake)
    #
    # start the service
    our_password = 'qweqwe'
    usr_password = 'wrong'
    r.nc_start_service(
        ip='does not matter',
        port=1234,
        password=our_password)
    #
    # check starting position
    assert 0 == r.count_please_tcp_boot()
    #
    # scenario: user sends an invalid password
    r.nc_gruel_recv(
        d_gruel=gruel_puff.unpack(
            bb=gruel_press.create_client_login_bb(
                password=usr_password,
                heartbeat_interval=3)))
    orb.cycle()
    #
    # check effects: we should boot the client
    assert server_customs_cog.state == ServerCustomsState.reject_stage_a
    assert 0 == r.count_gruel_send()
    #
    return True

@test
def should_do_successful_login_accept():
    engine = fake_engine_new()
    clock = engine.get_clock()
    gruel_protocol = gruel_protocol_new()
    gruel_press = gruel_press_new(
        gruel_protocol=gruel_protocol,
        mtu=engine.mtu)
    gruel_puff = gruel_puff_new(
        gruel_protocol=gruel_protocol,
        mtu=engine.mtu)
    #
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST_GRUEL_SERVER)
    server_customs_cog = orb.init_cog(
        construct=server_customs_cog_new)
    r = orb.init_cog(
        construct=receiver_cog_fake)
    #
    # start the service
    our_password = 'qweqwe'
    r.nc_start_service(
        ip='does not matter',
        port=1234,
        password=our_password)
    #
    # scenario: user sends an valid password
    r.nc_gruel_recv(
        d_gruel=gruel_puff.unpack(
            bb=gruel_press.create_client_login_bb(
                password=our_password,
                heartbeat_interval=3)))
    orb.cycle()
    #
    # confirm effects
    assert server_customs_cog.state == ServerCustomsState.authorised
    assert 1 == r.count_announce_login()
    assert 1 == r.count_gruel_send()
    d_grual = gruel_puff.unpack(r.last_gruel_send())
    assert d_grual['message_h'] == 'server_greet'
    #
    return True

@test
def should_run_a_rejection_sequence():
    engine = fake_engine_new()
    clock = engine.get_clock()
    gruel_protocol = gruel_protocol_new()
    gruel_press = gruel_press_new(
        gruel_protocol=gruel_protocol,
        mtu=engine.mtu)
    gruel_puff = gruel_puff_new(
        gruel_protocol=gruel_protocol,
        mtu=engine.mtu)
    #
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST_GRUEL_SERVER)
    server_customs_cog = orb.init_cog(
        construct=server_customs_cog_new)
    r = orb.init_cog(
        construct=receiver_cog_fake)
    #
    # start the service
    our_password = 'qweqwe'
    usr_password = 'wrong'
    r.nc_start_service(
        ip='does not matter',
        port=1234,
        password=our_password)
    #
    # confirm effects: see a 
    assert 0 == clock.now()
    #
    # scenario: rejection is sequenced
    server_customs_cog._to_rejection(
        s='triggered by test')
    #
    # nothing should have changed
    assert 0 == r.count_gruel_send()
    assert 0 == r.count_please_tcp_boot()
    #
    # at three seconds we should see server_bye but no boot
    clock.inc(3)
    orb.cycle()
    assert 1 == r.count_gruel_send()
    d_gruel = gruel_puff.unpack(
        bb=r.last_gruel_send())
    assert d_gruel['message_h'] == 'server_bye'
    assert 0 == r.count_please_tcp_boot()
    #
    # at four seconds we should see the boot
    clock.inc(1)
    orb.cycle()
    assert 1 == r.count_please_tcp_boot()
    #
    return True

@test
def should_clear_state_in_announce_connect():
    engine = fake_engine_new()
    clock = engine.get_clock()
    gruel_protocol = gruel_protocol_new()
    gruel_press = gruel_press_new(
        gruel_protocol=gruel_protocol,
        mtu=engine.mtu)
    gruel_puff = gruel_puff_new(
        gruel_protocol=gruel_protocol,
        mtu=engine.mtu)
    #
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST_GRUEL_SERVER)
    server_customs_cog = orb.init_cog(
        construct=server_customs_cog_new)
    r = orb.init_cog(
        construct=receiver_cog_fake)
    #
    r.nc_announce_tcp_connect(
        ip='does not matter',
        port=1234)
    assert 1 == r.count_nearnote()
    #
    r.nc_announce_tcp_condrop()
    assert 2 == r.count_nearnote()
    #
    return True

@test
def should_buffer_a_couple_of_docs():
    engine = fake_engine_new()
    clock = engine.get_clock()
    gruel_protocol = gruel_protocol_new()
    gruel_press = gruel_press_new(
        gruel_protocol=gruel_protocol,
        mtu=engine.mtu)
    gruel_puff = gruel_puff_new(
        gruel_protocol=gruel_protocol,
        mtu=engine.mtu)
    #
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST_GRUEL_SERVER)
    server_customs_cog = orb.init_cog(
        construct=server_customs_cog_new)
    r = orb.init_cog(
        construct=receiver_cog_fake)
    #
    # start the service
    our_password = 'qweqwe'
    r.nc_start_service(
        ip='does not matter',
        port=1234,
        password=our_password)
    #
    # preparation: user logs in
    r.nc_announce_tcp_connect(
        ip='also not important',
        port=456)
    r.nc_gruel_recv(
        d_gruel=gruel_puff.unpack(
            bb=gruel_press.create_client_login_bb(
                password=our_password,
                heartbeat_interval=3)))
    orb.cycle()
    #
    # scenario: user sends part of a doc
    r.nc_gruel_recv(
        d_gruel=gruel_puff.unpack(
            bb=gruel_press.create_docdata_bb(
                b_complete=0,
                data='123')))
    orb.cycle()
    #
    # confirm effects (doc is not complete, so should be no effects)
    assert 0 == r.count_doc_recv()
    #
    # scenario: now finish the first doc
    r.nc_gruel_recv(
        d_gruel=gruel_puff.unpack(
            bb=gruel_press.create_docdata_bb(
                b_complete=1,
                data='456')))
    orb.cycle()
    #
    # confirm effects (doc is not complete, so should be no effects)
    assert 1 == r.count_doc_recv()
    assert r.last_doc_recv() == '123456'
    #
    # scenario: now send a second doc, and check it's correct
    r.nc_gruel_recv(
        d_gruel=gruel_puff.unpack(
            bb=gruel_press.create_docdata_bb(
                b_complete=1,
                data='here is a doc')))
    orb.cycle()
    #
    # confirm effects
    assert 2 == r.count_doc_recv()
    assert r.last_doc_recv() == 'here is a doc'
    #
    return True

@test
def should_send_a_couple_of_docs():
    engine = fake_engine_new()
    clock = engine.get_clock()
    gruel_protocol = gruel_protocol_new()
    gruel_press = gruel_press_new(
        gruel_protocol=gruel_protocol,
        mtu=engine.mtu)
    gruel_puff = gruel_puff_new(
        gruel_protocol=gruel_protocol,
        mtu=engine.mtu)
    #
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST_GRUEL_SERVER)
    server_customs_cog = orb.init_cog(
        construct=server_customs_cog_new)
    r = orb.init_cog(
        construct=receiver_cog_fake)
    #
    # start the service
    our_password = 'qweqwe'
    r.nc_start_service(
        ip='does not matter',
        port=1234,
        password=our_password)
    #
    # preparation: user logs in
    r.nc_announce_tcp_connect(
        ip='also not important',
        port=456)
    r.nc_gruel_recv(
        d_gruel=gruel_puff.unpack(
            bb=gruel_press.create_client_login_bb(
                password=our_password,
                heartbeat_interval=3)))
    orb.cycle()
    #
    # confirm assumptions
    assert 1 == r.count_gruel_send()
    #
    # scenario: we send a large outbound document towards customs
    doc = '/'.join( ['x', 'y'*2000, 'z'] )
    r.nc_doc_send(
        doc=doc)
    #
    # confirm effects: expect to see the doc broken up into several pieces
    assert 2 <= r.count_gruel_send()
    # examine first doc packet
    d_gruel = gruel_puff.unpack(r.get_gruel_send()[1])
    assert d_gruel['message_h'] == 'docdata'
    assert d_gruel['b_complete'] == 0
    assert d_gruel['data'][0] == 'x'
    # examine next-to-last doc packet
    d_gruel = gruel_puff.unpack(r.get_gruel_send()[-2])
    assert d_gruel['message_h'] == 'docdata'
    assert d_gruel['b_complete'] == 0
    assert d_gruel['data'][-1] == 'y'
    # examine last doc packet
    d_gruel = gruel_puff.unpack(r.get_gruel_send()[-1])
    assert d_gruel['message_h'] == 'docdata'
    assert d_gruel['b_complete'] == 1
    assert d_gruel['data'][-1] == 'z'
    #
    return True

@test
def should_convert_heartbeat_requests_to_gruel():
    engine = fake_engine_new()
    clock = engine.get_clock()
    gruel_protocol = gruel_protocol_new()
    gruel_press = gruel_press_new(
        gruel_protocol=gruel_protocol,
        mtu=engine.mtu)
    gruel_puff = gruel_puff_new(
        gruel_protocol=gruel_protocol,
        mtu=engine.mtu)
    #
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST_GRUEL_SERVER)
    server_customs_cog = orb.init_cog(
        construct=server_customs_cog_new)
    r = orb.init_cog(
        construct=receiver_cog_fake)
    #
    # start the service
    our_password = 'qweqwe'
    r.nc_start_service(
        ip='does not matter',
        port=1234,
        password=our_password)
    #
    # preparation: user logs in
    r.nc_announce_tcp_connect(
        ip='also not important',
        port=456)
    r.nc_gruel_recv(
        d_gruel=gruel_puff.unpack(
            bb=gruel_press.create_client_login_bb(
                password=our_password,
                heartbeat_interval=3)))
    orb.cycle()
    #
    # starting asumptions
    assert 1 == r.count_gruel_send()
    #
    # scenario: we get a request to heartbeat
    r.nc_heartbeat_send()
    #
    # confirm effects
    assert 2 == r.count_gruel_send()
    d_gruel = gruel_puff.unpack(r.get_gruel_send()[-1])
    assert d_gruel['message_h'] == 'heartbeat'
    #
    return True

if __name__ == '__main__':
    run_tests()

