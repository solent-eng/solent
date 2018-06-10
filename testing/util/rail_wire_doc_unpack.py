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

from solent import run_tests
from solent import test
from solent.util import RailWireDocUnpack

import sys

class Receiver:
    def __init__(self):
        self.events = []
    def cb_wire_doc_unpack_head(self, cs_wire_doc_unpack_head):
        zero_h = cs_wire_doc_unpack_head.zero_h
        doc_len = cs_wire_doc_unpack_head.doc_len
        #
        self.events.append( ('head', zero_h, doc_len) )
    def cb_wire_doc_unpack_done(self, cs_wire_doc_unpack_done):
        zero_h = cs_wire_doc_unpack_done.zero_h
        bb = cs_wire_doc_unpack_done.bb
        #
        self.events.append( ('done', zero_h, bb) )

@test
def should_test_basics():
    r = Receiver()

    rail_wire_doc_unpack = RailWireDocUnpack()
    rail_wire_doc_unpack.zero(
        zero_h='test_basics',
        cb_wire_doc_unpack_head=r.cb_wire_doc_unpack_head,
        cb_wire_doc_unpack_done=r.cb_wire_doc_unpack_done)

    def create_send_data():
        l = []
        # leading uint64, big-endian
        l.extend([int(n) for n in '00 00 00 00 00 00 00 07'.split()])
        # some content. note that there are two bytes more than then
        # stated length above.
        l.extend([ord(c) for c in 'abcdefghi'])
        return bytes(l)

    bb_send = create_send_data()

    # There are fifteen test bytes. We send them in in batches.
    assert 2 == rail_wire_doc_unpack.accept(bb_send[0:2])
    assert 0 == len(r.events)

    assert 4 == rail_wire_doc_unpack.accept(bb_send[2:6])
    assert 0 == len(r.events)

    assert 3 == rail_wire_doc_unpack.accept(bb_send[6:9])
    assert 1 == len(r.events)
    assert r.events[-1] == ('head', 'test_basics', 7)

    assert 3 == rail_wire_doc_unpack.accept(bb_send[9:12])
    assert 1 == len(r.events)

    assert 3 == rail_wire_doc_unpack.accept(bb_send[12:17])
    assert 2 == len(r.events)
    assert r.events[-1] == ('done', 'test_basics', bytes('abcdefg', 'ascii'))

    # Wire string should throw an error if you make a fresh call to it
    # after it has called back with done.
    b_caught = False
    try:
        rail_wire_doc_unpack.accept(bb_send[15:17])
    except:
        b_caught = True
    assert b_caught == True

    return True

if __name__ == '__main__':
    run_tests()
