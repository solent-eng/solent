#
# gruel_press tests
#
# // note
# There are more extensive tests of this found in prop_gruel_client. The
# reason is that this class and the gruel puff are heavily related, and it
# seemed straightforward to develop them against one another. (This does leave
# open the possibility for bugs where they're both wrong, but for this stage
# in the project it's OK. If there's bugs, we will get to them.)
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
def test_client_login_creation():
    gruel_schema = gruel_schema_new()
    gruel_press = gruel_press_new(
        mtu=500,
        gruel_schema=gruel_schema)
    #
    message_h = 'client_login'
    #
    message_stencil = gruel_schema.get_message_stencil(
        message_h=message_h)
    payload = gruel_press.create_client_login_payload(
        username='uname',
        password='password_value')
    '''
    print(hexdump_bytearray(
        arr=payload))
    '''
    #
    return True

@test
def test_server_greet_creation():
    gruel_schema = gruel_schema_new()
    gruel_press = gruel_press_new(
        mtu=500,
        gruel_schema=gruel_schema)
    #
    message_h = 'server_greet'
    #
    message_stencil = gruel_schema.get_message_stencil(
        message_h=message_h)
    payload = gruel_press.create_server_greet_payload()
    '''
    print(hexdump_bytearray(
        arr=payload))
    '''
    #
    return True

@test
def test_server_bye_creation():
    gruel_schema = gruel_schema_new()
    gruel_press = gruel_press_new(
        mtu=500,
        gruel_schema=gruel_schema)
    #
    message_h = 'server_bye'
    #
    message_stencil = gruel_schema.get_message_stencil(
        message_h=message_h)
    payload = gruel_press.create_server_bye_payload()
    '''
    print(hexdump_bytearray(
        arr=payload))
    '''
    #
    return True

@test
def test_heartbeat_creation():
    gruel_schema = gruel_schema_new()
    gruel_press = gruel_press_new(
        mtu=500,
        gruel_schema=gruel_schema)
    #
    message_h = 'heartbeat'
    #
    message_stencil = gruel_schema.get_message_stencil(
        message_h=message_h)
    payload = gruel_press.create_heartbeat_payload()
    '''
    print(hexdump_bytearray(
        arr=payload))
    '''
    #
    return True

@test
def test_docdata_creation():
    gruel_schema = gruel_schema_new()
    gruel_press = gruel_press_new(
        mtu=500,
        gruel_schema=gruel_schema)
    #
    message_h = 'docdata'
    #
    message_stencil = gruel_schema.get_message_stencil(
        message_h=message_h)
    payload = gruel_press.create_docdata_payload(
        b_doc_terminates=1,
        sender_doc_h='sender_01',
        payload='some content for the payload block')
    '''
    print(hexdump_bytearray(
        arr=payload))
    '''
    #
    return True

if __name__ == '__main__':
    run_tests(
        unders_file=sys.modules['__main__'].__file__)

