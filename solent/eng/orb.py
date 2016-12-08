#
# orb
#
# // overview
# The orb is a mechanism that supplies an answer to two questions.
# 1) Business logic lives in cogs. But you don't want them registered directly
# with the engine. If they were, how would they communicate with one another?
# Imagine if you got some data in from the network, and then wanted to send it
# to a file-writer cog - what then?
# 2) The engine contains an event loop. But how to harness this power? How
# does an application get access to it?
#
# An orb satisfies these needs:
# 1) It provides a nearcast. That is, a mechanism by which cogs can talk to
# one another without requiring knowlede of each other's internal state.
# 2) It bridges power from the engine to groups of cogs. On each pass of its
# event loop, an engine will run through its list of registered orbs and call
# orb.at_turn. The orb will then call the at_turn method for any cog that
# offers it.
#
# If you've made it this far, you might appreciate this feature of an orb:
# It's possible for multiple logical applications to run in a single process
# and under a single engine. Once we have this model in place, it becomes
# trivial to scale applications by moving them off nearcasts (single system)
# and onto broadcasts (multiple pieces of hardware) with zero changes to
# business logic.
#
# There's a bit going on here. It could be more explained with a short video
# and some lego. To be done.
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

from .activity import activity_new
from .test_receiver_cog import test_receiver_cog_new

from solent.log import log
from solent.util import uniq

from collections import deque
from collections import OrderedDict as od
import inspect
from pprint import pprint
import types

class Orb:
    def __init__(self, engine, nearcast_schema, snoop):
        self.engine = engine
        self.nearcast_schema = nearcast_schema
        self.snoop = snoop
        #
        self.cogs = []
        self.pending = deque()
    def at_turn(self, activity):
        #
        self.distribute()
        #
        if self.snoop:
            self.snoop.at_turn(
                activity=activity)
        for cog in self.cogs:
            if 'at_turn' in dir(cog):
                fn_at_turn = getattr(cog, 'at_turn')
                fn_at_turn(
                    activity=activity)
    def cycle(self, max_turns=20):
        '''
        This is useful for testing. It keeps calling at_turn until there
        is no more activity left to do. You probably do not want an engine
        using this behaviour, because it would lead to starvation of other
        orbs.
        '''
        turn_counter = 0
        activity = activity_new()
        while True:
            self.at_turn(
                activity=activity)
            if activity.get():
                # clears, and then we do another circuit of the while loop
                activity.clear()
            else:
                break
            if max_turns != None and turn_counter >= max_turns:
                log('breaking orb.cycle (reached maxturns %s)'%(
                    max_turns))
                break
            turn_counter += 1
    def add_cog(self, cog):
        if cog in self.cogs:
            try:
                name = cog.cog_h
            except:
                name = 'unknown, has no cog_h'
            raise Exception("Cog %s is already added."%(name))
        self.cogs.append(cog)
    def init_cog(self, construct):
        cog = construct(
            cog_h='cog_%s_%s'%(uniq(), construct.__name__),
            orb=self,
            engine=self.engine)
        self.add_cog(
            cog=cog)
        return cog
    def init_test_receiver_cog(self):
        cog = test_receiver_cog_new(
            nearcast_schema=self.nearcast_schema,
            cog_h='test_receiver',
            orb=self,
            engine=self.engine)
        self.add_cog(
            cog=cog)
        return cog
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
            if self.snoop:
                self.snoop.on_nearcast_message(
                    cog_h=cog_h,
                    message_h=message_h,
                    d_fields=d_fields)
            for cog in self.cogs:
                if rname in dir(cog):
                    fn = getattr(cog, rname)
                    try:
                        fn(**d_fields)
                    except:
                        log('problem is %s:%s'%(cog.cog_h, rname))
                        raise

def orb_new(engine, nearcast_schema, snoop=None):
    ob = Orb(
        engine=engine,
        nearcast_schema=nearcast_schema,
        snoop=snoop)
    return ob

