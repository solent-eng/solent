#
# gruel_puff
#
# // overview
# Used for expanding gruel-protocol messages from their wire form into
# something that is useful to application software.
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

from .gruel_protocol import Datatype
from .gruel_protocol import gmt_value_to_name

from solent.log import hexdump_bytes

import struct

class GruelPuff:
    def __init__(self, gruel_protocol, mtu):
        self.gruel_protocol = gruel_protocol
        self.mtu = mtu
    def unpack(self, bb):
        #
        # The first byte is the message identifier. We need to get this out in
        # order to determine what message stencil we are going to use
        first_byte_value = struct.unpack_from('!B', bb, 0)[0]
        message_stencil = self.gruel_protocol.get_message_stencil_from_fmt_id(
            gmt_id=first_byte_value)
        #
        d_message = {}
        offset = 0
        for (field_name, field_dt) in message_stencil.items():
            if field_dt == Datatype.u1:
                value_tpl = struct.unpack_from('!B', bb, offset)
                value = value_tpl[0]
                offset += 1
            elif field_dt == Datatype.u2:
                value_tpl = struct.unpack_from('!H', bb, offset)
                value = value_tpl[0]
                offset += 2
            elif field_dt == Datatype.vs:
                value_tpl = struct.unpack_from('!H', bb, offset)
                vs_len = value_tpl[0]
                offset += 2
                value_tpl = struct.unpack_from(
                    '%ss'%(vs_len),
                    bb,
                    offset)
                value = str(value_tpl[0].partition(b'\0')[0], 'utf8')
                offset += vs_len
            else:
                raise Exception("Unhandled datatype %s"%(field_dt))
            d_message[field_name] = value
        #
        # this is useful for unit tests
        if 'message_h' not in d_message:
            d_message['message_h'] = gmt_value_to_name(
                value=first_byte_value)
        return d_message

def gruel_puff_new(gruel_protocol, mtu):
    ob = GruelPuff(
        gruel_protocol=gruel_protocol,
        mtu=mtu)
    return ob

