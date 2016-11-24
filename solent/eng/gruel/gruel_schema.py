#
# Protocol definition for GRUEL.
#
# // overview
# This module contains both the protocol definition, and a schema object
# that allows your application to get easy access to that schema.
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

from solent.util import uniq
from solent.util.interface_script import SignalConsumer, init_interface_script_parser

from collections import OrderedDict as od
from enum import Enum
from pprint import pprint

class Datatype(Enum):
    u1 = uniq()
    u2 = uniq()
    # fixed size-string, 40 bytes
    s40 = uniq()
    # fixed size-string, 100 bytes
    s100 = uniq()
    # variable string (u2 tells payload length, then payload)
    vs = uniq()

class MessageType(Enum):
    client_login = 0
    server_greet = 1
    server_bye = 2
    heartbeat = 3
    docdata = 4

I_MESSAGE_DEF = '''
    i message h
        i u1 field_h
        i u2 field_h
        i s40 field_h
        i s100 field_h
        i vs field_h

    message client_login
        u1 message_type
        u1 seconds_between_heartbeats
        # This is useful for situations where you have routing limitations
        # between yourself and the server venue.
        u2 max_packet_len_in_bytes
        # This mechanism is in here to prevent a situation where a single
        # client could run a denial-of-service attack on a server by causing
        # the server to buffer an infinate amount of doc data. It indicates
        # what the maximum doc size could be (which might span several docdata
        # messages, but must be within a well-defined maximum size).
        u2 max_doc_size_in_bytes
        s100 protocol_h
        s100 username
        s100 password
        s100 notes

    message server_greet
        u1 message_type
        # If this number comes back and is smaller than what the client wrote
        # in client_login, then the client must adjust down to this size.
        u2 max_packet_len_in_bytes
        # If this number comes back and is smaller than what the client wrote
        # in client_login, then the client must adjust down to this size.
        u2 max_doc_size_in_bytes
        vs notes

    message server_bye
        u1 message_type
        vs notes

    message heartbeat
        u1 message_type

    message docdata
        u1 message_type
        # set to true in the last packet of each document
        u1 b_doc_terminates
        s40 sender_doc_id
        vs payload
'''

class MessageStencil:
    def __init__(self, message_h):
        self.message_h = message_h
        # name vs datatype
        self.fields = od()
    def add_field_stencil(self, name, dt):
        if name in self.fields:
            raise Exception('dupe field in msg [%s]'%name)
        self.fields[name] = dt
    def dt_for_field(self, field_h):
        return self.fields[field_h].name
    def field_names(self):
        return self.fields.keys()
    def field_datatypes(self):
        return [dt.name for dt in self.fields.values()]
    def items(self):
        '''
        For each field, returns (field_name, field_dt).
        '''
        return self.fields.items()
    def __repr__(self):
        sb = []
        for (n, dt) in self.fields.items():
            sb.append('%s(%s)'%(n, dt))
        return '|'.join(sb)

class GruelSchema:
    '''
    Holds stencils for the kinds of messages that are supported
    in the schema of the gruel messaging protoco.
    '''
    def __init__(self, d_message_stencils):
        self.d_message_stencils = d_message_stencils
    def __contains__(self, key):
        return key in self.d_message_stencils
    def get_message_type_enum(self):
        return MessageType
    def get_message_stencil(self, message_h):
        return self.d_message_stencils[message_h]

def gruel_schema_new():
    '''
    You should only need to create one of these per application. The
    structure of the schema is stored in the module itself, hence there
    is no needf for arguments.
    '''
    class Acc(SignalConsumer):
        def __init__(self):
            self.d_message_stencils = od()
            self.current_message = None
        #
        def on_message(self, h):
            if h in self.d_message_stencils:
                raise Exception('duplicate definition for [%s]'%h)
            ob = MessageStencil(
                message_h=h)
            self.d_message_stencils[h] = ob
            self.current_message = ob
        def on_u1(self, field_h):
            self.current_message.add_field_stencil(
                name=field_h,
                dt=Datatype.u1)
        def on_u2(self, field_h):
            self.current_message.add_field_stencil(
                name=field_h,
                dt=Datatype.u2)
        def on_s40(self, field_h):
            self.current_message.add_field_stencil(
                name=field_h,
                dt=Datatype.s40)
        def on_s100(self, field_h):
            self.current_message.add_field_stencil(
                name=field_h,
                dt=Datatype.s100)
        def on_vs(self, field_h):
            self.current_message.add_field_stencil(
                name=field_h,
                dt=Datatype.vs)
    acc = Acc()
    parser = init_interface_script_parser(acc)
    parser.parse(I_MESSAGE_DEF)
    #
    ob = GruelSchema(
        d_message_stencils=acc.d_message_stencils)
    return ob

