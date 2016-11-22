#
# Protocol definition for GRUEL.
#
# --------------------------------------------------------
#   :license
# --------------------------------------------------------
#
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
# .
#
# --------------------------------------------------------
#   :head
# --------------------------------------------------------
from solent.util import uniq
from solent.util.interface_script import SignalConsumer, init_interface_script_parser

from collections import OrderedDict as od
from pprint import pprint

DT_UINT8 = uniq()
DT_UINT16 = uniq()
DT_S40 = uniq()
DT_S100 = uniq()
DT_VS = uniq()

I_MESSAGE_DEF = '''
    i message h
        i uint8 field_h
        i uint16 field_h
        # fixed size-string, 40 bytes
        i s40 field_h
        # fixed size-string, 100 bytes
        i s100 field_h
        # variable string (uint16 tells payload length, then payload)
        i vs field_h


    message client_greet
        uint8 message_type
        uint8 seconds_between_heartbeats
        uint16 max_packet_len_in_bytes
        uint16 max_doc_size_in_bytes
        s100 protocol_h
        s100 username
        s100 password
        s100 notes

    message server_greet
        uint8 message_type
        uint16 max_packet_len
        uint16 max_doc_size
        vs notes

    message client_logout
        uint8 message_type
        vs notes

    message server_bye
        uint8 message_type
        vs notes

    message heartbeat
        uint8 message_type

    message docdata
        uint8 message_type
        # set to true in the last packet of each document
        uint8 b_doc_terminates
        s40 sender_doc_id
        vs payload
'''

# --------------------------------------------------------
#   :interface_script
# --------------------------------------------------------
class Message:
    def __init__(self):
        # name vs datatype
        self.fields = od()
    def add(self, name, dt):
        if name in self.fields:
            raise Exception('dupe field in msg [%s]'%name)
        self.fields[name] = dt
    def __repr__(self):
        sb = []
        for (n, dt) in self.fields.items():
            sb.append('%s(%s)'%(n, dt))
        return '|'.join(sb)

def proto_gruel_schema():
    '''
    Accumulate plan_i notation into an existing canon_plan_orb, giving it
    its structure.
    '''
    class Acc(SignalConsumer):
        def __init__(self):
            self.messages = od()
            self.current_message = None
        #
        def on_message(self, h):
            if h in self.messages:
                raise Exception('duplicate definition for [%s]'%h)
            ob = Message()
            self.messages[h] = ob
            self.current_message = ob
        def on_uint8(self, field_h):
            self.current_message.add(
                name=field_h,
                dt=DT_UINT8)
        def on_uint16(self, field_h):
            self.current_message.add(
                name=field_h,
                dt=DT_UINT16)
        def on_s40(self, field_h):
            self.current_message.add(
                name=field_h,
                dt=DT_S40)
        def on_s100(self, field_h):
            self.current_message.add(
                name=field_h,
                dt=DT_S100)
        def on_vs(self, field_h):
            self.current_message.add(
                name=field_h,
                dt=DT_VS)
    acc = Acc()
    parser = init_interface_script_parser(acc)
    parser.parse(I_MESSAGE_DEF)
    return acc.messages

def proto_gruel_pack(schema, byte_array, message_h, fields*):
    schema = 
    if message
    

