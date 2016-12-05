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
from testing.gruel.receiver_cog import receiver_cog_fake

from solent.eng import activity_new
from solent.eng import cs
from solent.gruel import gruel_puff_new
from solent.gruel import gruel_press_new
from solent.gruel import gruel_schema_new
from solent.gruel import prop_gruel_server_new
from solent.log import log
from solent.log import hexdump_bytearray
from solent.util import uniq

import sys

MTU = 1492

def start_server(engine, prop_gruel_server, addr, port, password):
    prop_gruel_server.start(
        addr=addr,
        port=port,
        password=password)

def stop_server(prop_gruel_server):
    prop_gruel_server.stop()

@test
def should_construct_and_start_and_stop():
    addr = '127.0.0.1'
    port = 5000
    username = 'dssd'
    password = 'fgfdgf'
    r = receiver_cog_fake(
        cog_h='receiver',
        orb=None,
        engine=None)
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
        cb_doc_recv=r.on_doc_recv)
    #
    # scenario: start and stop without crashing
    start_server(
        engine=engine,
        prop_gruel_server=prop_gruel_server,
        addr=addr,
        port=port,
        password=password)
    stop_server(
        prop_gruel_server=prop_gruel_server)
    #
    return True

if __name__ == '__main__':
    run_tests(
        unders_file=sys.modules['__main__'].__file__)

