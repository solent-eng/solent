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

from solent.test import run_tests
from solent.test import test
from solent.util import RailBytesetter

import sys

class Receiver:
    def __init__(self):
        self.events = []
    def cb_bytesetter_pack(self, cs_bytesetter_pack):
        bb = cs_bytesetter_pack.bb
        #
        msg = bb.decode('utf8')
        self.events.append( ('pack', msg) )
    def cb_bytesetter_fini(self, cs_bytesetter_fini):
        self.events.append( ('fini', '') )

@test
def should_work_when_supplied_string_is_aligned():
    r = Receiver()
    #
    mtu = 8
    rail_bytesetter = RailBytesetter()
    rail_bytesetter.zero(
        cb_bytesetter_pack=r.cb_bytesetter_pack,
        cb_bytesetter_fini=r.cb_bytesetter_fini,
        mtu=mtu,
        bytesetter_h='does not matter')
    #
    # step: add 20 bytes of information
    rail_bytesetter.write(
        bb=bytes('0123456789012345', 'utf8'))
    rail_bytesetter.flush()
    #
    # verify: we should have had two callbacks
    assert 3 == len(r.events)
    assert r.events == [
        ('pack', '01234567'),
        ('pack', '89012345'),
        ('fini', '')]
    #
    return True

@test
def should_work_when_supplied_string_is_not_aligned():
    r = Receiver()
    #
    mtu = 8
    rail_bytesetter = RailBytesetter()
    rail_bytesetter.zero(
        cb_bytesetter_pack=r.cb_bytesetter_pack,
        cb_bytesetter_fini=r.cb_bytesetter_fini,
        mtu=mtu,
        bytesetter_h='does not matter')
    #
    # step: add 20 bytes of information
    rail_bytesetter.write(
        bb=bytes('0123456789012345678901', 'utf8'))
    #
    # verify: we should have had two callbacks
    assert 2 == len(r.events)
    assert r.events == [
        ('pack', '01234567'),
        ('pack', '89012345')]
    #
    # step: call end
    rail_bytesetter.flush()
    #
    # verify: we should have had a further two callback, one for
    # last few bytes, and then a 'fini' callback.
    assert 4 == len(r.events)
    assert r.events[-2] == ('pack', '678901')
    assert r.events[-1] == ('fini', '')
    #
    return True

if __name__ == '__main__':
    run_tests()
