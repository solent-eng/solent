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

from solent.gruel import gruel_press_new
from solent.gruel import gruel_protocol_new
from solent.log import hexdump_bytes
from solent.log import hexdump_string
from solent.test import run_tests
from solent.test import test

import sys

@test
def test_creation():
    gruel_protocol = gruel_protocol_new()
    gruel_press = gruel_press_new(
        mtu=1400,
        gruel_protocol=gruel_protocol)
    return True

@test
def test_client_login_creation():
    gruel_protocol = gruel_protocol_new()
    gruel_press = gruel_press_new(
        mtu=500,
        gruel_protocol=gruel_protocol)
    #
    message_h = 'client_login'
    #
    message_stencil = gruel_protocol.get_message_stencil(
        message_h=message_h)
    bb = gruel_press.create_client_login_bb(
        password='password_value',
        heartbeat_interval=1)
    '''
    print(hexdump_bytes(
        arr=bb))
    '''
    #
    return True

@test
def test_server_greet_creation():
    gruel_protocol = gruel_protocol_new()
    gruel_press = gruel_press_new(
        mtu=500,
        gruel_protocol=gruel_protocol)
    #
    message_h = 'server_greet'
    #
    message_stencil = gruel_protocol.get_message_stencil(
        message_h=message_h)
    bb = gruel_press.create_server_greet_bb(
        max_packet_size=800)
    '''
    print(hexdump_bytes(
        arr=bb))
    '''
    #
    return True

@test
def test_server_bye_creation():
    gruel_protocol = gruel_protocol_new()
    gruel_press = gruel_press_new(
        mtu=500,
        gruel_protocol=gruel_protocol)
    #
    message_h = 'server_bye'
    #
    message_stencil = gruel_protocol.get_message_stencil(
        message_h=message_h)
    bb = gruel_press.create_server_bye_bb(
        notes='notes for server_bye')
    '''
    print(hexdump_bytes(
        arr=bb))
    '''
    #
    return True

@test
def test_heartbeat_creation():
    gruel_protocol = gruel_protocol_new()
    gruel_press = gruel_press_new(
        mtu=500,
        gruel_protocol=gruel_protocol)
    #
    message_h = 'heartbeat'
    #
    message_stencil = gruel_protocol.get_message_stencil(
        message_h=message_h)
    bb = gruel_press.create_heartbeat_bb()
    '''
    print(hexdump_bytes(
        arr=bb))
    '''
    #
    return True

@test
def test_docdata_creation():
    gruel_protocol = gruel_protocol_new()
    gruel_press = gruel_press_new(
        mtu=500,
        gruel_protocol=gruel_protocol)
    #
    message_h = 'docdata'
    #
    message_stencil = gruel_protocol.get_message_stencil(
        message_h=message_h)
    bb = gruel_press.create_docdata_bb(
        b_complete=1,
        data='some content for the bb block')
    '''
    print(hexdump_bytes(
        arr=bb))
    '''
    #
    return True

if __name__ == '__main__':
    run_tests()

