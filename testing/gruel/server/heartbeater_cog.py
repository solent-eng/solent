#
# heartbeater (testing)
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

from solent import uniq
from solent.eng import activity_new
from solent.eng.cs import *
from solent.gruel import gruel_protocol_new
from solent.gruel import gruel_press_new
from solent.gruel import gruel_puff_new
from solent.gruel.server.nearcast import I_NEARCAST_GRUEL_SERVER
from solent.gruel.server.heartbeater_cog import heartbeater_cog_new
from solent.gruel.server.server_customs_cog import server_customs_cog_new
from solent.gruel.server.server_customs_cog import ServerCustomsState
from solent import log
from solent.test import run_tests
from solent.test import test

from enum import Enum
import sys

MTU = 500

@test
def should_start_on_announce_login_and_stop_on_announce_condrop():
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
    heartbeater_cog = orb.init_cog(
        construct=heartbeater_cog_new)
    r = orb.init_testbridge()
    #
    # check starting assumptions
    assert 0 == r.count_heartbeat_send()
    #
    # scenario: time passes with no client logged in
    clock.inc(10)
    #
    # confirm effects
    assert 0 == r.count_heartbeat_send()
    #
    # scenario: client connects and one second passes
    r.nc_announce_login(
        max_packet_size=1400,
        max_fulldoc_size=20000)
    clock.inc(5)
    orb.cycle()
    #
    # confirm effects: we should see a heartbeat
    assert 1 == r.count_heartbeat_send()
    #
    # scenario: more than a second passes
    clock.inc(5)
    orb.cycle()
    #
    # confirm effects: we should see a new heartbeat
    assert 2 == r.count_heartbeat_send()
    #
    # scenario: condrop happens, and more time passes
    r.nc_announce_tcp_condrop()
    clock.inc(10)
    orb.cycle()
    #
    # confirm effects: we should see no new heartbeats
    assert 2 == r.count_heartbeat_send()
    #
    return True

if __name__ == '__main__':
    run_tests()

