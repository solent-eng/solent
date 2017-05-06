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
from testing.util import clock_fake

from solent.redis import rail_resp_etcher_new

import sys

class Receiver:
    def __init__(self):
        self.events = []
    def cb_etch_head(self, cs_etch_head):
        self.events.append(
            ('head', ''))
    def cb_etch_tail(self, cs_etch_tail):
        self.events.append(
            ('tail', ''))
    def cb_etch_pack(self, cs_etch_pack):
        bb = cs_etch_pack.bb
        #
        msg = bb.decode('utf8')
        self.events.append(
            ('pack', msg))

@test
def should_do_basic_int_pack():
    mtu = 100
    #
    r = Receiver()
    #
    rail_resp_etcher = rail_resp_etcher_new(
        mtu=mtu,
        cb_etch_head=r.cb_etch_head,
        cb_etch_tail=r.cb_etch_tail,
        cb_etch_pack=r.cb_etch_pack)
    #
    # step: write an int
    rail_resp_etcher.open(
        etch_h='identifier')
    rail_resp_etcher.etch_int(
        n=17)
    rail_resp_etcher.close()
    #
    # vali: check int format
    assert 3 == len(r.events)
    assert r.events[0] == ('head', '')
    assert r.events[1] == ('pack', ':17\r\n')
    assert r.events[2] == ('tail', '')
    #
    return True

@test
def should_do_basic_err_pack():
    mtu = 100
    #
    r = Receiver()
    #
    rail_resp_etcher = rail_resp_etcher_new(
        mtu=mtu,
        cb_etch_head=r.cb_etch_head,
        cb_etch_tail=r.cb_etch_tail,
        cb_etch_pack=r.cb_etch_pack)
    #
    # step: write an int
    rail_resp_etcher.open(
        etch_h='identifier')
    rail_resp_etcher.etch_err(
        msg='Sample Err')
    rail_resp_etcher.close()
    #
    # vali: check int format
    assert 3 == len(r.events)
    assert r.events[0] == ('head', '')
    assert r.events[1] == ('pack', '-Sample Err\r\n')
    assert r.events[2] == ('tail', '')
    #
    return True

@test
def should_do_simple_string_pack():
    mtu = 100
    #
    r = Receiver()
    #
    rail_resp_etcher = rail_resp_etcher_new(
        mtu=mtu,
        cb_etch_head=r.cb_etch_head,
        cb_etch_tail=r.cb_etch_tail,
        cb_etch_pack=r.cb_etch_pack)
    #
    # step: write an int
    rail_resp_etcher.open(
        etch_h='identifier')
    rail_resp_etcher.etch_short_string(
        msg='Sample string')
    rail_resp_etcher.close()
    #
    # vali: check int format
    assert 3 == len(r.events)
    assert r.events[0] == ('head', '')
    assert r.events[1] == ('pack', '+Sample string\r\n')
    assert r.events[2] == ('tail', '')
    #
    return True

@test
def should_do_complex_string_pack():
    mtu = 100
    #
    r = Receiver()
    #
    rail_resp_etcher = rail_resp_etcher_new(
        mtu=mtu,
        cb_etch_head=r.cb_etch_head,
        cb_etch_tail=r.cb_etch_tail,
        cb_etch_pack=r.cb_etch_pack)
    #
    # step: write an int
    rail_resp_etcher.open(
        etch_h='identifier')
    rail_resp_etcher.etch_string("123")
    rail_resp_etcher.close()
    #
    # vali: check int format
    assert 3 == len(r.events)
    assert r.events[0] == ('head', '')
    assert r.events[1] == ('pack', '$3\r\n123\r\n')
    assert r.events[2] == ('tail', '')
    #
    return True

@test
def should_handle_arrays():
    mtu = 100
    #
    r = Receiver()
    #
    rail_resp_etcher = rail_resp_etcher_new(
        mtu=mtu,
        cb_etch_head=r.cb_etch_head,
        cb_etch_tail=r.cb_etch_tail,
        cb_etch_pack=r.cb_etch_pack)
    #
    # step: write an int
    rail_resp_etcher.open(
        etch_h='identifier')
    rail_resp_etcher.etch_array(3)
    rail_resp_etcher.etch_int(1)
    rail_resp_etcher.etch_int(2)
    rail_resp_etcher.etch_int(3)
    rail_resp_etcher.etch_int(0)
    rail_resp_etcher.close()
    #
    # vali: check int format
    assert 3 == len(r.events)
    assert r.events[0] == ('head', '')
    assert r.events[1] == ('pack', '*3\r\n:1\r\n:2\r\n:3\r\n:0\r\n')
    assert r.events[2] == ('tail', '')
    #
    return True

if __name__ == '__main__':
    run_tests(
        unders_file=sys.modules['__main__'].__file__)

