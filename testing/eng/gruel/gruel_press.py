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

from solent.eng import gruel_press_new
from solent.eng import gruel_schema_new
from solent.log import hexdump_bytearray
from solent.log import hexdump_string

import sys

@test
def test_creation():
    gruel_schema = gruel_schema_new()
    gruel_press = gruel_press_new(
        mtu=1400,
        gruel_schema=gruel_schema)
    return True

@test
def test_login_message_creation():
    gruel_schema = gruel_schema_new()
    gruel_press = gruel_press_new(
        mtu=500,
        gruel_schema=gruel_schema)
    #
    message_h = 'client_login'
    #
    arr = gruel_press.get_bytearray()
    message_stencil = gruel_schema.get_message_stencil(
        message_h=message_h)
    MessageType = gruel_schema.get_message_type_enum()
    gruel_press.apply(
        message_h=message_h,
        message_type=MessageType.client_login.value,
        seconds_between_heartbeats=1,
        max_packet_len_in_bytes=1490,
        max_doc_size_in_bytes=1400,
        protocol_h='proto_h',
        username='uname',
        password='password_value',
        notes='text for notes')
    '''
    print(hexdump_string(
        s=' 0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789abcdefghijklmnop'))
    '''
    print(hexdump_bytearray(
        arr=arr))
    #
    return True

if __name__ == '__main__':
    run_tests(
        unders_file=sys.modules['__main__'].__file__)

