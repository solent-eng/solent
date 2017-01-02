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

from solent import SolentQuitException
from solent.log import log
from solent.util import uniq

from collections import deque
from collections import OrderedDict as od
import inspect
from pprint import pprint
import types

class LogSnoop:
    '''
    Logs any message seen on the associated nearcast.
    '''
    def __init__(self, orb, nearcast_schema):
        self.orb = orb
        self.nearcast_schema = nearcast_schema
        #
        self.b_enabled = True
    def close(self):
        pass
    def disable(self):
        self.b_enabled = False
    def at_turn(self, activity):
        pass
    def on_nearcast_message(self, cog_h, message_h, d_fields):
        if not self.b_enabled:
            return
        def format_message():
            sb = []
            sb.append('[%s/%s] %s'%(self.orb.orb_h, cog_h, message_h))
            for key in self.nearcast_schema[message_h]:
                sb.append('%s:%s'%(key, d_fields[key]))
            return '/'.join(sb)
        nice = format_message()
        log(nice)

class NetworkSnoop:
    '''
    This gives you a network service that allows you to use netcat or similar
    to see all the messages that are passing through the nearcast. Useful
    for debugging. The snoop behaves a lot like a cog, but has different
    construction arrangements.

    Allows a user to snoop on the messages on a nearcast.
    
    This class is similar to a cog. However, the mechanism by which it
    receives nearcast messages is different to cogs. Cogs implement an
    on_message_h method. Whereas this gets everything in on_nearcast_message.
    And that requires special logic in the orb.

    This behaves like a blocking server (only one client at a time).
    '''
    def __init__(self, orb, nearcast_schema, engine, addr, port):
        self.orb = orb
        self.nearcast_schema = nearcast_schema
        self.engine = engine
        self.addr = addr
        self.port = port
        #
        self.server_sid = None
        self.client_sid = None
        self.q_outbound = None
        #
        self._open_server()
    def close(self):
        self._close_server()
    def at_turn(self, activity):
        if self.q_outbound:
            activity.mark(
                l=self,
                s='processing q_outbound')
            while self.q_outbound:
                payload = bytes(
                    source=self.q_outbound.popleft(),
                    encoding='utf8')
                self.engine.send(
                    sid=self.client_sid,
                    payload=payload)
    #
    def _open_server(self):
        self.server_sid = self.engine.open_tcp_server(
            addr=self.addr,
            port=self.port,
            cb_tcp_connect=self.engine_on_tcp_connect,
            cb_tcp_condrop=self.engine_on_tcp_condrop,
            cb_tcp_recv=self.engine_on_tcp_recv)
    def _close_server(self):
        self.engine.close_tcp_server(
            sid=self.server_sid)
        self.server_sid = None
    #
    def engine_on_tcp_connect(self, cs_tcp_connect):
        engine = cs_tcp_connect.engine
        client_sid = cs_tcp_connect.client_sid
        addr = cs_tcp_connect.addr
        port = cs_tcp_connect.port
        #
        self._close_server()
        self.q_outbound = deque()
        self.client_sid = client_sid
        log("connect/[snoop]/%s/%s/%s"%(
            client_sid,
            addr,
            port))
    def engine_on_tcp_condrop(self, cs_tcp_condrop):
        engine = cs_tcp_condrop.engine
        client_sid = cs_tcp_condrop.client_sid
        message = cs_tcp_condrop.message
        #
        log("condrop/[snoop]/%s/%s"%(client_sid, message))
        self.client_sid = None
        self.q_outbound = None
        self._open_server()
    def engine_on_tcp_recv(self, cs_tcp_recv):
        engine = cs_tcp_recv.engine
        client_sid = cs_tcp_recv.client_sid
        data = cs_tcp_recv.data
        #
        pass
    #
    def on_nearcast_message(self, cog_h, message_h, d_fields):
        if not self.client_sid:
            return
        def format_message():
            sb = []
            sb.append('[%s/%s] %s'%(self.orb.orb_h, cog_h, message_h))
            for key in self.nearcast_schema[message_h]:
                sb.append('%s:%s'%(key, d_fields[key]))
            return '/'.join(sb)
        nice = format_message()
        self.q_outbound.append(nice)

class Orb:
    def __init__(self, orb_h, engine, nearcast_schema):
        self.orb_h = orb_h
        self.engine = engine
        self.nearcast_schema = nearcast_schema
        #
        self.snoops = []
        self.pins = []
        self.cogs = []
        self.pending = deque()
    def close(self):
        for snoop in self.snoops:
            if 'close' in dir(snoop):
                snoop.close()
        for cog in self.cogs:
            if 'close' in dir(cog):
                cog.close()
    def at_turn(self, activity):
        #
        self.distribute()
        #
        for snoop in self.snoops:
            snoop.at_turn(
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
    def add_network_snoop(self, addr, port):
        self.snoops.append(
            NetworkSnoop(
                orb=self,
                nearcast_schema=self.nearcast_schema,
                engine=self.engine,
                addr=addr,
                port=port))
    def add_log_snoop(self):
        self.snoops.append(
            LogSnoop(
                orb=self,
                nearcast_schema=self.nearcast_schema))
    def init_pin(self, construct):
        '''
        construct must have no arguments, and will typically be the __init__
        method of a pin class. (No arguments is deliberate. It discourages
        abuse. Their purpose is to listen for things, not to act on
        information. Acting is done by cogs.)
        '''
        pin = construct()
        #
        # validate that the pin's on_methods match the schema
        on_methods = [m for m in dir(pin) if m.startswith('on_')]
        for om_name in on_methods:
            method = getattr(pin, om_name)
            args = inspect.getargspec(method).args
            if args[0] != 'self':
                raise Exception("pin method %s should have arg 'self'."%(
                    om_name))
            args = args[1:]
            message_h = om_name[3:]
            if not self.nearcast_schema.has_message(message_h):
                m = "Cog has %s but there is no message %s in schema."%(
                    om_name, message_h)
                raise Exception(m)
            desired_args = self.nearcast_schema.get_args_for_message(
                message_h=message_h)
            if desired_args != args:
                sb = [ "Nearcast schema message %s"%(message_h)
                     , "defines these args: [%s]"%('|'.join(desired_args))
                     , "but %s.%s"%(pin.__class__.__name__, om_name)
                     , "params are inconsistent: [%s]"%('|'.join(args))
                     ]
                raise Exception(' '.join(sb))
        #
        self.pins.append(pin)
        return pin
    def _add_cog(self, cog):
        if cog in self.cogs:
            try:
                name = cog.cog_h
            except:
                name = 'unknown, has no cog_h'
            raise Exception("Cog %s is already added."%(name))
        #
        # validate the cog's on_methods match the schema
        cog_h = cog.cog_h
        on_methods = [m for m in dir(cog) if m.startswith('on_')]
        for om_name in on_methods:
            method = getattr(cog, om_name)
            args = inspect.getargspec(method).args
            if args[0] != 'self':
                raise Exception("cog method %s should have arg 'self'."%(
                    om_name))
            args = args[1:]
            message_h = om_name[3:]
            if not self.nearcast_schema.has_message(message_h):
                m = "Cog has %s but there is no message %s in schema."%(
                    om_name, message_h)
                raise Exception(m)
            desired_args = self.nearcast_schema.get_args_for_message(
                message_h=message_h)
            if desired_args != args:
                sb = [ "Nearcast schema message %s"%(message_h)
                     , "defines these args: [%s]"%('|'.join(desired_args))
                     , "but %s.%s"%(cog_h, om_name)
                     , "params are inconsistent: [%s]"%('|'.join(args))
                     ]
                raise Exception(' '.join(sb))
        #
        self.nearcast_schema.attach_nearcast_dispatcher_on_cog(
            orb=self,
            cog=cog)
        self.cogs.append(cog)
    def init_cog(self, construct):
        cog = construct(
            cog_h=construct.__name__,
            orb=self,
            engine=self.engine)
        self._add_cog(
            cog=cog)
        return cog
    def init_test_receiver_cog(self):
        cog = test_receiver_cog_new(
            nearcast_schema=self.nearcast_schema,
            cog_h='test_receiver',
            orb=self,
            engine=self.engine)
        self._add_cog(
            cog=cog)
        return cog
    def nearcast(self, cog, message_h, **d_fields):
        '''
        It is important that we buffer all the messages to be sequenced, and
        then actually send them out later on in distribute. Otherwise we can
        end up in a situation where actors have hijacked activity away from
        the event loop, and a starvation scenario.
        '''
        if 'cog_h' not in dir(cog):
            raise Exception("Looks like an invalid cog arg. Has no cog_h. %s"%(
                str(cog)))
        elif None == cog:
            cog_h = 'None'
        else:
            cog_h = cog.cog_h
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
            for snoop in self.snoops:
                snoop.on_nearcast_message(
                    cog_h=cog_h,
                    message_h=message_h,
                    d_fields=d_fields)
            for pin in self.pins:
                if rname in dir(pin):
                    fn = getattr(pin, rname)
                    try:
                        fn(**d_fields)
                    except SolentQuitException:
                        raise
                    except:
                        log('')
                        log('!! breaking in pin, %s:%s'%(
                            cog.__class__.__name__, rname))
                        log('')
                        raise
            for cog in self.cogs:
                if rname in dir(cog):
                    fn = getattr(cog, rname)
                    try:
                        fn(**d_fields)
                    except SolentQuitException:
                        raise
                    except:
                        log('')
                        log('!! breaking in cog, %s:%s'%(cog.cog_h, rname))
                        log('')
                        raise

def orb_new(orb_h, engine, nearcast_schema):
    ob = Orb(
        orb_h=orb_h,
        engine=engine,
        nearcast_schema=nearcast_schema)
    return ob

