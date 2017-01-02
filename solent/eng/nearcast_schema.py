#
# nearcast schema
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

from solent.log import log
from solent.util import ns
from solent.util.interface_script import init_interface_script_parser
from solent.util.interface_script import SignalConsumer

from collections import OrderedDict as od

I_NEARCAST_EXAMPLE = '''
    i message h
        i field h

    # declare a message called organisation that takes certain fields
    message organisation
        field h
        field name
        field address

    # declare a message called person that takes certain fields
    message person
        field h
        field firstname
        field lastname
        field age
        field organisation_h
'''

class NearcastSignalConsumer(SignalConsumer):
    '''
    User for converting interface script into a nearcast schema.

    Interface script accumulator. Imagine someone is writing some interface
    script to describe their nearcast. This is the interface that they will be
    talking to.
    '''
    def __init__(self):
        self.messages = od()
        self.current_message_lst = None
    def on_message(self, h):
        if h in self.messages:
            raise Exception('duplicate definition for [%s]'%h)
        lst = []
        self.messages[h] = lst
        self.current_message_lst = lst
    def on_field(self, h):
        if None == self.current_message_lst:
            raise Exception('Need to define a message before fields.')
        self.current_message_lst.append(h)

class NearcastSchema:
    '''
    Captures the message schema of a nearcast group.

    This is basically a wrapper for an ordered dictionary. It contains
    messages. The reason I've done it up as its own class is to present
    an more obvious interface to anyone who is interacting with this
    code.

    Note that a nearcast schema is quite a bit simpler than the schema you'd
    use for a broadcast, or for a bespoke protocol. The reason for this: we
    don't need to serialise the message, meaning there is a bunch of type
    information that we can dispense with.
    '''
    def __init__(self, d_messages):
        self.messages = d_messages
    def has_message(self, name):
        return name in self.messages
    def get_args_for_message(self, message_h):
        return self.messages[message_h]
    def get_messages(self):
        return self.messages
    def exists(self, message_h):
        if message_h in self.messages:
            return True
        return False
    def __contains__(self, item):
        return item in self.messages.keys()
    def __getitem__(self, key):
        return self.messages[key]
    def attach_nearcast_dispatcher_on_cog(self, orb, cog):
        '''
        This attaches a variable called nearcast to a cog so that cog code can
        nearcast just by saying "self.nearcast.message_h(args)". This is a lot
        less hassle than typing "self.orb.nearcast", and then having to supply
        the cog itself, the message_h, and then the arguments.

        Essentially, this gives the semantics of python functions to nearcast
        messages. Which is pretty damn cool.

        The mechanism here is ugly. Unimportant. When we move to a typed
        language, there's several ways we could handle this: inheritance, use
        of macros.
        '''
        if 'nearcast' in dir(cog):
            raise Exception("Cog %s already has a member 'nearcast'."%(
                cog.cog_h))
        sb = []
        sb.append('class DynamicNearcastDispatcher:')
        sb.append('    def __init__(self, orb, cog):')
        sb.append('        self.orb = orb')
        sb.append('        self.cog = cog')
        for (message_h, fields) in self.messages.items():
            if fields:
                args = ', '.join(fields)
                sb.append('    def %s(self, %s):'%(message_h, args))
            else:
                sb.append('    def %s(self):'%(message_h))
            sb.append('        self.orb.nearcast(')
            sb.append('            cog=self.cog,')
            sb.append("            message_h='%s',"%message_h)
            for field in fields:
                sb.append('            %s=%s,'%(field, field))
            sb.append('            )')
        sb.append('')
        sb.append('''globals()['DynamicNearcastDispatcher'] = DynamicNearcastDispatcher''')
        sb.append('')
        code = '\n'.join(sb)
        exec(code)
        nearcast_dispatcher = DynamicNearcastDispatcher(
            orb=orb,
            cog=cog)
        setattr(cog, 'nearcast', nearcast_dispatcher)

def nearcast_schema_new(i_nearcast):
    '''
    i_nearcast: text in interface script format. It will need to match the
    dialect described by NearcastSignalConsumer in this module. Look in
    nearcast.py for an example of some interface script

    This class will return a dictionary. Keys are the names of messages. Each
    value is a list of field names. (This is sufficient for describing a
    nearcast schema)
    '''
    signal_consumer = NearcastSignalConsumer()
    parser = init_interface_script_parser(
        signal_consumer=signal_consumer)
    parser.parse(i_nearcast)
    nearcast_schema = NearcastSchema(
        d_messages=signal_consumer.messages)
    return nearcast_schema

