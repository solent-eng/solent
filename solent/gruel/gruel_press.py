#
# gruel press
#
# // overview
# converts data into a gruel message that is ready for the wire
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

from .gruel_schema import GruelMessageType

from solent.log import log
from solent.log import hexdump_bytes

import struct

MAX_PACKET_LEN_IN_BYTES = 1400
MAX_FULLDOC_SIZE_IN_BYTES = 0

PROTOCOL_H = 'proto_h/change_me_later'

class GruelPress:
    def __init__(self, gruel_schema, mtu):
        self.gruel_schema = gruel_schema
        self.mtu = mtu
        #
        # This is the block of memory we will render to. Emphasis: a single
        # array of memory is used to prepare messages for the wire. (So you
        # would not want to buffer this anywhere.)
        self.arr = bytearray(self.mtu)
    def create(self, message_h, **fields):
        '''
        Render the supplied message values to the bytearray.
        '''
        #
        # ensure that the fields match the schema
        if message_h not in self.gruel_schema:
            raise Exception("No message exists matching [%s]"%message_h)
        message_stencil = self.gruel_schema.get_message_stencil(
            message_h=message_h)
        set_sch = set(message_stencil.field_names())
        set_got = set(fields.keys())
        if set_sch != set_got:
            raise Exception("Inconsistent fields/want:%s/got:%s"%(
                str(set_sch), str(set_got)))
        #
        # render
        offset = 0
        for (field_h, field_dt) in message_stencil.items():
            field_value = fields[field_h]
            # struct docs: https://docs.python.org/3.1/library/struct.html
            #log('** o%s press %s %s'%(offset, field_h, field_value))
            if field_dt.name == 'u1':
                bsize = 1
                struct.pack_into(
                    '!B',        # fmt. B is unsigned char
                    self.arr,    # buffer
                    offset,      # offset
                    field_value)
                offset += bsize
            elif field_dt.name == 'u2':
                bsize = 2
                struct.pack_into(
                    '!H',        # fmt. H is unsigned short
                    self.arr,    # buffer
                    offset,      # offset
                    field_value)
                offset += bsize
            elif field_dt.name == 'vs':
                s_len = len(field_value)
                # first we do a two-byte length, network-endian
                bsize = 2
                struct.pack_into(
                    '!H',        # fmt. H is unsigned short
                    self.arr,    # buffer
                    offset,      # offset
                    s_len)
                offset += bsize
                # Now we put that string into the array. Emphasis: these
                # strings are not zero-terminated.
                struct.pack_into(
                    '%ss'%s_len, # fmt.
                    self.arr,    # buffer
                    offset,      # offset
                    bytes(field_value, 'utf8'))
                offset += s_len
            else:
                raise Exception("Datatype not recognised/handled: %s"%(
                    field_dt.name))
        return self.arr
    #
    def create_client_login_payload(self, password, heartbeat_interval):
        gmt = GruelMessageType.client_login
        #
        message_h = gmt.name
        message_type = gmt.value
        self.create(
            message_h=message_h,
            # fields are below
            message_type=message_type,
            heartbeat_interval=heartbeat_interval,
            max_packet_size=MAX_PACKET_LEN_IN_BYTES,
            max_fulldoc_size=MAX_FULLDOC_SIZE_IN_BYTES,
            protocol_h=PROTOCOL_H,
            password=password,
            notes='text for notes')
        return self.arr
    def create_server_greet_payload(self, max_packet_size):
        gmt = GruelMessageType.server_greet
        #
        message_h = gmt.name
        message_type = gmt.value
        self.create(
            message_h=message_h,
            # fields are below
            message_type=message_type,
            max_packet_size=max_packet_size,
            max_fulldoc_size=MAX_FULLDOC_SIZE_IN_BYTES,
            notes='text for notes')
        return self.arr
    def create_server_bye_payload(self, notes):
        gmt = GruelMessageType.server_bye
        #
        message_h = gmt.name
        message_type = gmt.value
        self.create(
            message_h=message_h,
            # fields are below
            message_type=message_type,
            notes=notes)
        return self.arr

    def create_heartbeat_payload(self):
        gmt = GruelMessageType.heartbeat
        #
        message_h = gmt.name
        message_type = gmt.value
        self.create(
            message_h=message_h,
            # fields are below
            message_type=message_type)
        return self.arr
    def create_docdata_payload(self, b_complete, data):
        gmt = GruelMessageType.docdata
        #
        message_h = gmt.name
        message_type = gmt.value
        self.create(
            message_h=message_h,
            # fields are below
            message_type=message_type,
            b_complete=b_complete,
            data=data)
        return self.arr

def gruel_press_new(gruel_schema, mtu):
    ob = GruelPress(
        gruel_schema=gruel_schema,
        mtu=mtu)
    return ob

