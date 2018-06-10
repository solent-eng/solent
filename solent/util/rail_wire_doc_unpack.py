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
#
# // overview
# This is a simple unpacker for {wire string form}. Wire string form is a
# uint64 indicating length, followed by that number of bytes.

from solent import ns as Ns

import struct

class RailWireDocUnpack:

    def __init__(self):
        self.cs_wire_doc_unpack_head = Ns()
        self.cs_wire_doc_unpack_done = Ns()

        self.b_done = None
        self.buf = []
        self.n = None

    def call_wire_doc_unpack_head(self, zero_h, doc_len):
        self.cs_wire_doc_unpack_head.zero_h = zero_h
        self.cs_wire_doc_unpack_head.doc_len = doc_len
        self.cb_wire_doc_unpack_head(
            cs_wire_doc_unpack_head=self.cs_wire_doc_unpack_head)

    def call_wire_doc_unpack_done(self, zero_h, bb):
        self.cs_wire_doc_unpack_done.zero_h = zero_h
        self.cs_wire_doc_unpack_done.bb = bb
        self.cb_wire_doc_unpack_done(
            cs_wire_doc_unpack_done=self.cs_wire_doc_unpack_done)

    def zero(self, zero_h, cb_wire_doc_unpack_head, cb_wire_doc_unpack_done):
        self.zero_h = zero_h
        self.cb_wire_doc_unpack_head = cb_wire_doc_unpack_head
        self.cb_wire_doc_unpack_done = cb_wire_doc_unpack_done

        self.buf.clear()
        self.b_done = False

    def accept(self, bb):
        '''Returns the length of bytes that it accepted.
        '''
        if self.b_done:
            raise Exception("Have already returned as done.")

        idx = 0

        # Accumulate the string length. This is the first 8 byes.
        if self.n == None:
            while len(self.buf) < 8:
                if idx >= len(bb):
                    return idx

                b = bb[idx]
                idx += 1

                self.buf.append(b)

            if idx > len(bb):
                return idx

            # Work out our string length
            assert 8 == len(self.buf)

            uint64 = bytes(self.buf)
            self.buf.clear()

            self.n = struct.unpack('!Q', uint64)[0]
            self.call_wire_doc_unpack_head(
                zero_h=self.zero_h,
                doc_len=self.n)

        # Accumulate our string
        while len(self.buf) < self.n:
            if idx >= len(bb):
                return idx

            b = bb[idx]
            idx += 1

            self.buf.append(b)

            if len(self.buf) == self.n:
                bb = bytes(self.buf)
                self.buf.clear()

                self.call_wire_doc_unpack_done(
                    zero_h=self.zero_h,
                    bb=bytes(bb))

                self.b_done = True
                break

        return idx

