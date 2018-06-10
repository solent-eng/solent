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

from solent.base.sip import Sip

from solent import ref_create
from solent import ref_lookup
from solent import ref_acquire
from solent import ref_release
from solent import log
from solent import hexdump
from solent import run_tests
from solent import test

@test
def should_handle_c():
    sip = Sip(100)
    sip.put_unsigned_char(
        c='q',
        o=16)
    n = sip.get_unsigned_char(
        o=16)
    assert n == 'q'
    #
    return True

@test
def should_handle_u1():
    sip = Sip(100)
    sip.put_u1(
        n=123,
        o=20)
    n = sip.get_u1(
        o=20)
    assert n == 123
    #
    return True

@test
def should_handle_u2():
    sip = Sip(100)
    sip.put_u2(
        n=123,
        o=24)
    n = sip.get_u2(
        o=24)
    assert n == 123
    #
    return True

@test
def should_handle_u4():
    sip = Sip(100)
    sip.put_u4(
        n=123,
        o=4)
    n = sip.get_u4(
        o=4)
    assert n == 123
    #
    return True

@test
def should_handle_u8():
    sip = Sip(100)
    sip.put_u8(
        n=123,
        o=8)
    n = sip.get_u8(
        o=8)
    assert n == 123
    #
    return True

@test
def should_lookup_bytes_easily():
    sip = Sip(100)
    #
    # Remember: sips store numbers as network format (big endian).
    sip.put_u4(
        n=0x55,
        o=28)
    assert sip[28] == 0x00
    assert sip[29] == 0x00
    assert sip[30] == 0x00
    assert sip[31] == 0x55
    #
    return True

@test
def should_write_string():
    sip = Sip(100)
    #
    # In UTF8, the delta symbol takes two bytes (\xce\x94').
    delta_symbol = u'\N{GREEK CAPITAL LETTER DELTA}'
    assert 1 == len(delta_symbol)
    delta_len = len(delta_symbol.encode('utf8'))
    assert 2 == delta_len
    #
    # Length of the source string, in characters.
    source = u'abcdefghi%s'%(delta_symbol)
    source_string_len = len(source)
    assert 10 == source_string_len
    #
    # Length of the source string, in bytes
    utf8_bytes = bytes(source.encode('utf8'))
    assert 11 == len(utf8_bytes)
    #
    # Store in the arr
    sip.store_vs(
        o=10,
        arr=utf8_bytes)
    assert 11 == sip.get_vslen(
        o=10)
    #
    # String from the arr
    log('!! %s'%(sip.get_vs(10)))
    assert source == sip.get_vs(
        o=10)
    #
    # Fetch from the arr. Currently we're not testing that this is correct.
    second = bytearray(sip.get_vslen(o=10))
    sip.fetch_vs(
        o=10,
        arr=second)
    assert second == utf8_bytes
    #
    return True

@test
def should_store_and_retrieve_reference():
    sip = Sip(100)
    #
    source_a = 'abcdefghij'
    source_b = 'z'*50000
    ref_a = ref_create(
        bb=source_a)
    ref_b = ref_create(
        bb=source_b)
    #
    sip.put_ref(
        ref=ref_a,
        o=0)
    sip.put_ref(
        ref=ref_b,
        o=8)
    #
    ref_m = sip.get_ref(0)
    ref_n = sip.get_ref(8)
    print('n %s'%ref_n)
    print('b %s'%ref_b)
    assert ref_m == ref_a
    assert ref_n == ref_b
    #
    return True

@test
def should_clone_equivalent_sip():
    content = b'abcdefghij'
    sip_b = Sip(10)
    sip_b.clone(
        bb=content)
    hexdump(content, title='content')
    hexdump(sip_b.arr, title='sip_b')
    assert sip_b.arr == content
    #
    return True

@test
def should_clone_shorter_sip():
    content = b'abcdefghij'
    clen = len(content)
    sip = Sip(100)
    sip.clone(
        bb=content)
    hexdump(content, title='content')
    hexdump(sip.arr, title='sip')
    assert sip.arr[:clen] == content
    #
    return True

if __name__ == '__main__':
    run_tests()

