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
# This rail arranges bytes into fixed-size blocks. This could be useful if you
# were consuming a stream of bytes from a source, and seeking to output these
# bytes to a series of fixed-size network packets.

from solent.log import hexdump_bytes
from solent.log import log

from collections import deque

class CsBytesetterPack:
    def __init__(self):
        self.bytesetter_h = None
        self.bb = None

class CsBytesetterFini:
    def __init__(self):
        self.bytesetter_h = None

class RailBytesetter:
    def __init__(self):
        self.blst = deque()
        self.cs_bytesetter_pack = CsBytesetterPack()
        self.cs_bytesetter_fini = CsBytesetterFini()
    def zero(self, mtu, cb_bytesetter_pack, cb_bytesetter_fini, bytesetter_h):
        self.mtu = mtu
        self.cb_bytesetter_pack = cb_bytesetter_pack
        self.cb_bytesetter_fini = cb_bytesetter_fini
        self.bytesetter_h = bytesetter_h
        #
        self.blst.clear()
        #
        self.bsize = 0
    #
    def write(self, bb):
        self.blst.append(bb)
        self.bsize += len(bb)
        #
        while self.bsize >= self.mtu:
            self._dispatch_pack()
    def flush(self):
        while self.bsize > 0:
            self._dispatch_pack()
        self._call_bytesetter_fini(
            bytesetter_h=self.bytesetter_h)
    #
    def _call_bytesetter_pack(self, bytesetter_h, bb):
        self.cs_bytesetter_pack.bytesetter_h = bytesetter_h
        self.cs_bytesetter_pack.bb = bb
        self.cb_bytesetter_pack(
            cs_bytesetter_pack=self.cs_bytesetter_pack)
    def _call_bytesetter_fini(self, bytesetter_h):
        self.cs_bytesetter_fini.bytesetter_h = bytesetter_h
        self.cb_bytesetter_fini(
            cs_bytesetter_fini=self.cs_bytesetter_fini)
    #
    def _dispatch_pack(self):
        mtu = self.mtu
        #
        pack_size = min(self.bsize, mtu)
        #
        out = bytearray(pack_size)
        nail = 0
        remain = pack_size
        while remain > 0:
            bb = self.blst.popleft()
            if len(bb) > remain:
                use = bb[:remain]
                overflow = bb[remain:]
                self.blst.appendleft(overflow)
                bb = use
            #
            peri = nail+len(bb)
            out[nail:peri] = bb
            #
            remain -= len(bb)
            nail = peri
        #
        self._call_bytesetter_pack(
            bytesetter_h=self.bytesetter_h,
            bb=out)
        #
        self.bsize -= pack_size

