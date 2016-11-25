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

from solent.eng import activity_new
from solent.eng import cs
from solent.eng import gruel_puff_new
from solent.eng import gruel_press_new
from solent.eng import gruel_schema_new
from solent.eng import prop_gruel_client_new
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
def test_status_at_rest():
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
def test_attempt_connection():
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
def test_failed_tcp_connection():
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
def test_successful_tcp_connection():
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
def test_after_connection_attempts_logon():
    addr = '127.0.0.1'
    port = 4098
    #
    activity = activity_new()
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
    # once we have connection success, this should be the status
    assert prop_gruel_client.get_status() == 'ready_to_attempt_login'
    #
    # give it a turn so it can make its move towards logging in.
    prop_gruel_client.at_turn(
        activity=activity)
    #
    # confirm effects
    assert activity.get()[-1] == 'PropGruelClient/sending login'
    assert prop_gruel_client.get_status() == 'login_message_in_flight'
    #
    # and now confirm that the message actually is in flight
    assert 1 == len(engine.sent_data)
    #
    return True

if __name__ == '__main__':
    run_tests(
        unders_file=sys.modules['__main__'].__file__)

