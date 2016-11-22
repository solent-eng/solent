#
# nearcast orb
#
# // brief
# Short: Nearcasting is an in-process equivalent of broadcasting.
#
# Long: nearcasting is a mechanism for cogs to pass messages between one
# another. programming is typically made up of lots of point-to-point
# messaging. You can imagine cog_a saying cog_b.message_name(kv_pairs). This
# works differently: cog_a would say orb.nearcast(message_name, kv_pairs).
# Later in the event loop, the orb would be told to distribute the messages.
# It would look at each of its cogs to see if they have a method
# on_message_name. Each cog which has that form gets a copy of the message.
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
#

from solent.log import log
from solent.util import uniq

from collections import deque
from collections import OrderedDict as od
import inspect
from pprint import pprint

class NearcastOrb:
    def __init__(self, engine, nearcast_schema, nearcast_snoop):
        self.engine = engine
        self.nearcast_schema = nearcast_schema
        self.nearcast_snoop = nearcast_snoop
        #
        self.cogs = []
        self.pending = deque()
    def at_turn(self):
        activity = False
        #
        self.distribute()
        #
        if self.nearcast_snoop:
            res = self.nearcast_snoop.at_turn()
            if res:
                activity = True
        for cog in self.cogs:
            if 'at_turn' in dir(cog):
                fn = getattr(cog, 'at_turn')
                res = fn()
                if res:
                    activity = True
        return activity
    def add_cog(self, cog):
        self.cogs.append(cog)
    def nearcast(self, cog_h, message_h, **d_fields):
        '''
        It is important that we buffer all the messages to be sequenced, and
        then actually send them out later on in distribute. Otherwise we can
        end up in a situation where actors have hijacked activity away from
        the event loop, and a starvation scenario.
        '''
        if message_h not in self.nearcast_schema:
            raise Exception("Unknown message type, [%s]"%(message_h))
        mfields = self.nearcast_schema[message_h]
        if sorted(d_fields.keys()) != sorted(mfields):
            raise Exception('inconsistent fields. need %s. got %s'%(
                str(mfields), str(d_fields.keys())))
        self.pending.append( (cog_h, message_h, d_fields) )
    def distribute(self):
        '''
        The event loop should periodically call this. This message distributes
        pending nearcast messages from a buffer and out to the cogs.
        '''
        while self.pending:
            (cog_h, message_h, d_fields) = self.pending.popleft()
            rname = 'on_%s'%(message_h)
            if self.nearcast_snoop:
                self.nearcast_snoop.on_nearcast_message(
                    cog_h=cog_h,
                    message_h=message_h,
                    d_fields=d_fields)
            for cog in self.cogs:
                if rname in dir(cog):
                    fn = getattr(cog, rname)
                    fn(**d_fields)

def nearcast_orb_new(engine, nearcast_schema, nearcast_snoop=None):
    '''
    This returns an instance of an object that behaves like an orb, but which
    also has nearcast functionality in. Nearcasting is essentially an
    in-process mechanism that otherwise behaves a lot like broadcasting:
    a cog can nearcast, and then any other cogs attached to the same nearcast
    will get a copy of the message.
    '''
    ob = NearcastOrb(
        engine=engine,
        nearcast_schema=nearcast_schema,
        nearcast_snoop=nearcast_snoop)
    return ob

