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
# Implements a packer for the Redis RESP protocol, which is described at
# https://redis.io/topics/protocol
#

from solent.util import RailBytesetter

class CsEtchHead(object):
    def __init__(self):
        self.etch_h = None

class CsEtchTail(object):
    def __init__(self):
        self.etch_h = None

class CsEtchPack(object):
    def __init__(self):
        self.etch_h = None
        self.bb = None

STATE_IDLE = 'idle'
STATE_OPEN = 'open'

NEWLINE = '\r\n'

class RailRespEtcher:
    def __init__(self, mtu, cb_etch_head, cb_etch_tail, cb_etch_pack):
        self.mtu = mtu
        self.cb_etch_head = cb_etch_head
        self.cb_etch_tail = cb_etch_tail
        self.cb_etch_pack = cb_etch_pack
        #
        self.cs_etch_head = CsEtchHead()
        self.cs_etch_tail = CsEtchTail()
        self.cs_etch_pack = CsEtchPack()
        #
        self.rail_bytesetter = RailBytesetter()
        #
        self.etch_h = None
        self.state = STATE_IDLE
        self.array_depth = None
    def open(self, etch_h):
        if self.state == STATE_OPEN:
            raise Exception("etcher is already open as %s"%(
                self.etch_h))
        #
        self.etch_h = etch_h
        self.state = STATE_OPEN
        self.array_depth = 0
        #
        self.rail_bytesetter.zero(
            mtu=self.mtu,
            cb_bytesetter_pack=self.cb_bytesetter_pack,
            cb_bytesetter_fini=self.cb_bytesetter_fini,
            bytesetter_h='does not matter')
        #
        self._call_etch_head(
            etch_h=etch_h)
    def close(self):
        if self.state != STATE_OPEN:
            raise Exception("etcher is already open as %s"%(
                self.etch_h))
        #
        if 0 != self.array_depth:
            raise Exception("Array is still at depth %s"%self.array_depth)
        #
        self.rail_bytesetter.flush()
        #
        self.state = STATE_IDLE
        self.etch_h = None
    def etch_array(self, n):
        msg = ''.join( [
            '*', str(n), NEWLINE,
        ] )
        bb = bytes(msg, 'utf8')
        self.rail_bytesetter.write(
            bb=bb)
    def etch_int(self, n):
        msg = ''.join( [':', str(n), NEWLINE] )
        bb = bytes(msg, 'utf8')
        self.rail_bytesetter.write(
            bb=bb)
    def etch_err(self, msg):
        msg = ''.join( ['-', msg, NEWLINE] )
        bb = bytes(msg, 'utf8')
        self.rail_bytesetter.write(
            bb=bb)
    def etch_short_string(self, msg):
        msg = ''.join( ['+', msg, NEWLINE] )
        bb = bytes(msg, 'utf8')
        self.rail_bytesetter.write(
            bb=bb)
    def etch_null(self, msg):
        msg = ''.join( ['$', '-1', NEWLINE] )
        bb = bytes(msg, 'utf8')
        self.rail_bytesetter.write(
            bb=bb)
    def etch_string(self, msg):
        msg = ''.join( [
            '$', str(len(msg)), NEWLINE,
            msg, NEWLINE] )
        bb = bytes(msg, 'utf8')
        self.rail_bytesetter.write(
            bb=bb)
    #
    def cb_bytesetter_pack(self, cs_bytesetter_pack):
        bytesetter_h = cs_bytesetter_pack.bytesetter_h
        bb = cs_bytesetter_pack.bb
        #
        self._call_etch_pack(
            etch_h=self.etch_h,
            bb=bb)
    def cb_bytesetter_fini(self, cs_bytesetter_fini):
        bytesetter_h = cs_bytesetter_fini.bytesetter_h
        #
        self._call_etch_tail(
            etch_h=self.etch_h)
    #
    def _call_etch_head(self, etch_h):
        self.cs_etch_head.etch_h = etch_h
        self.cb_etch_head(
            cs_etch_head=self.cs_etch_head)
    def _call_etch_tail(self, etch_h):
        self.cs_etch_tail.etch_h = etch_h
        self.cb_etch_tail(
            cs_etch_tail=self.cs_etch_tail)
    def _call_etch_pack(self, etch_h, bb):
        self.cs_etch_pack.etch_h = etch_h
        self.cs_etch_pack.bb = bb
        self.cb_etch_pack(
            cs_etch_pack=self.cs_etch_pack)

def rail_resp_etcher_new(mtu, cb_etch_head, cb_etch_tail, cb_etch_pack):
    ob = RailRespEtcher(
        mtu=mtu,
        cb_etch_head=cb_etch_head,
        cb_etch_tail=cb_etch_tail,
        cb_etch_pack=cb_etch_pack)
    return ob

