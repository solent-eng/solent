#
# sip
#
# // overview
# Wrapper for a bytebuffer. Name is a pun, small volume of fluid that could
# be taken from a pool.
#
# Note that numbers are stored big-endian. This is convention for networks,
# and fine for everything else.
#
# On first-look, the behaviour of references may seem strange. This codebase
# is about using python to model a sequencer architecture, not about building
# the ultimate sequencer architecture in python. The references system is
# done knowingly, with goal of leaving option open to c-like pointers
# later. In particular, it's done to allow sips to be used for nearcasting
# large objects around. Since they're in the same process, there will be
# situations where this is desirable.
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

from .ref import ref_acquire
from .ref import ref_release

from solent.util import uniq

import struct

TWO16 = pow(2, 16)

class Sip:
    def __init__(self, size):
        self.size = size
        #
        self.arr = bytearray(size)
        #
        self._references = []
    def _cleanup(self):
        '''
        This is only needed in this python implementation, and it's to allow
        the reference store to clean up its memory once we no longer need
        its references. (In a C-like language, there is no garbage collector
        to worry about.)
        '''
        while self._references:
            ref = self._references.pop()
            ref_release(
                ref=ref)
    def __getitem__(self, key):
        'note: returns an int'
        return self.arr[key]
    def __len__(self):
        return len(self.arr)
    def get(self):
        return self.arr
    def clone(self, bb):
        '''Writes the bytes into the current sip. The supplied sip length must
        be less than or equal to this sip.
        '''
        if len(bb) > len(self):
            raise Exception('Supplied sip [%s] longer than current sip [%s]'%(
                len(bb), len(self)))
        self.arr[0:len(bb)] = bb
    def put_ref(self, ref, o):
        '''The intent of this is that we can knowingly serialise a reference
        to a large object. For example, consider a large statically-defined
        string. The way that we achieve this in this python implementation
        is a total hack that uses a weak-reference dictionary.
        
        The reference takes 8 bytes, and is a u8 underneath. This follows
        a common practice in 64-bit architectures of 8-byte pointers.
        '''
        self.put_u8(
            n=ref,
            o=o)
        ref_acquire(
            ref=ref)
        self._references.append(ref)
    def get_ref(self, o):
        return self.get_u8(
            o=o)
    def put_unsigned_char(self, c, o):
        n = ord(c)
        struct.pack_into(
            '!B',       # fmt. c is unsigned char
            self.arr,   # buffer
            o,          # offset
            n)          # value
    def get_unsigned_char(self, o):
        n = struct.unpack_from(
            '!B',       # fmt. B is unsigned char
            self.arr,   # buffer
            o)[0]       # offset
        return chr(n)
    def put_u1(self, n, o):
        struct.pack_into(
            '!B',       # fmt. B is unsigned char
            self.arr,   # buffer
            o,          # offset
            n)          # value
    def get_u1(self, o):
        return struct.unpack_from(
            '!B',       # fmt. B is unsigned char
            self.arr,   # buffer
            o)[0]       # offset
    def put_u2(self, n, o):
        struct.pack_into(
            '!H',       # fmt. B is uint16_t
            self.arr,   # buffer
            o,          # offset
            n)          # value
    def get_u2(self, o):
        return struct.unpack_from(
            '!H',       # fmt. B is uint16_t
            self.arr,   # buffer
            o)[0]       # offset
    def put_u4(self, n, o):
        struct.pack_into(
            '!I',       # fmt. I is uint32_t
            self.arr,   # buffer
            o,          # offset
            n)          # value
    def get_u4(self, o):
        return struct.unpack_from(
            '!I',       # fmt. I is uint32_t
            self.arr,   # buffer
            o)[0]       # offset
    def put_u8(self, n, o):
        struct.pack_into(
            '!Q',       # fmt. Q is unsigned long long
            self.arr,   # buffer
            o,          # offset
            n)          # value
    def get_u8(self, o):
        return struct.unpack_from(
            '!Q',       # fmt. Q is unsigned long long
            self.arr,   # buffer
            o)[0]       # offset
    def store_vs(self, arr, o):
        '''Writes a variable string.

        The way string storage works: we use the first two bytes to
        indicate how long the rest of the string will be. This avoids
        dealing with termination characters.
        '''
        assert isinstance(arr, (bytes, bytearray))
        #
        d = self.size - (len(arr) + o + 2)
        if d < 0:
            raise Exception('strlen (%s) is too long (room: %s)'%(len(arr), d))
        if len(arr) > TWO16:
            raise Exception('strlen (%s) is longer than %s'%(len(arr), TWO16))
        self.put_u2(
            n=len(arr),
            o=o)
        #
        start = o+2
        end = start+len(arr)
        self.arr[start:end] = arr
    def get_vslen(self, o):
        return self.get_u2(
            o=o)
    def get_vs_bytes(self, o):
        '''Returns a new instance of bytes'''
        sl = self.get_vslen(
            o=o)
        #
        start = o+2
        end = start + sl
        return bytes(self.arr[start:end])
    def get_vs(self, o=2):
        '''Returns a new string.'''
        barr = self.get_vs_bytes(o=o)
        return str(barr, 'utf8')
    def fetch_vs(self, arr, o):
        assert isinstance(arr, bytearray)
        #
        sl = self.get_vslen(
            o=o)
        #
        start = o+2
        end = start+sl
        arr[0:sl] = self.arr[start:end]

def sip_new(size):
    ob = Sip(
        size=size)
    return ob

