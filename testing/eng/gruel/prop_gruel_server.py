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
from solent.log import log
from solent.log import hexdump_bytearray
from solent.util import uniq

import sys

MTU = 1492

class Receiver:
    def __init__(self):
        self.nearnote = []
        self.docs = []
    def on_nearnote(self, s):
        self.nearnote.append(s)
    def latest(self):
        return self.nearnote[-1]
    def on_client_doc(self, doc):
        self.docs.append(doc)

def start_server(engine, prop_gruel_server, addr, port, username, password, receiver):
    prop_gruel_server.start(
        addr=addr,
        port=port,
        username=username,
        password=password)

@test
def should_construct_and_start_and_stop():
    addr = '127.0.0.1'
    port = 5000
    username = 'dssd'
    password = 'fgfdgf'
    receiver = Receiver()
    #
    engine = engine_fake()
    activity = activity_new()
    #
    # scenario: construction
    gruel_schema = gruel_schema_new()
    gruel_press = gruel_press_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    gruel_puff = gruel_puff_new(
        gruel_schema=gruel_schema,
        mtu=MTU)
    prop_gruel_server = prop_gruel_server_new(
        engine=engine,
        cb_nearnote=receiver.on_nearnote,
        cb_client_doc=receiver.on_client_doc)
    #
    # confirm effects
    prop_gruel_server.at_turn(
        activity=activity)
    assert 1 == len(receiver.nearnote)
    assert receiver.latest() == 'prop_gruel_server: nearcast_started'
    #
    # scenario: start server
    start_server(
        engine=engine,
        prop_gruel_server=prop_gruel_server,
        addr=addr,
        port=port,
        username=username,
        password=password,
        receiver=receiver)
    #
    # confirm effects
    prop_gruel_server.at_turn(
        activity=activity)
    assert 2 == len(receiver.nearnote)
    assert receiver.latest() == 'tcp_server_cog: listening'
    #
    # scenario: stop server
    prop_gruel_server.stop()
    #
    # confirm effects
    prop_gruel_server.at_turn(
        activity=activity)
    assert 3 == len(receiver.nearnote)
    assert receiver.latest() == 'tcp_server_cog: stopped'

if __name__ == '__main__':
    run_tests(
        unders_file=sys.modules['__main__'].__file__)

