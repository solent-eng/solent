#!/usr/bin/python -B
#
# Scenarios.
#
# [Welcome. This class intends to be the easy-to-use path for users who want
# to use eng.]
#
#
# --------------------------------------------------------
#   :faq
# --------------------------------------------------------
#
# // What is the purpose of eng?
#
# To wrap the Berkeley sockets API with a much friendlier interface that makes
# it fairly easy to create applications with sophisticated network needs.
#
#
# // How do I use eng?
#
# Find a scenario in function main below that matches what you are trying to
# do. These scenarios have dual uses. They're useful for eng developers to
# test scenarios when they are working on the system. And they're useful for
# application developers to learn-by-example.
#
#
# // What does sid mean? What is a sid?
#
# It's a reference to an engine-managed socket. In order to facade the
# Berkeley sockets API with a friendlier interface, it was necessary to
# completely encase all supported socket scenarios within the engine. Sid is a
# reference that the engine gives you to an engine-managed socket.
#
#
# // What's the deal with these cs objects I get in callbacks?
#
# See the header of cs.py for an explanation of these, and the pydoc of the
# classes in that module for individual explanations.
#
#
# // What is an orb?
#
# Thing of the engine a bit like the engine of a car. It powers a crankshaft.
# Anything in the car that needs to be powered by the engine hangs of the
# crankshaft. You can think of an orb (short for orbit) as being a ring of
# teeth on the crankshaft. This provides a means by which the power of the
# engine can be distributed to things that want to consume that power.
#
# Every pass of the event loop, the engine calls orb.at_turn on each orb.
#
# Typically, an orb will be a container for a set of related services. (cogs,
# see below)
#
# The scenarios below show how to build an orb so that it operates cogs.
#
#
# // What is a cog?
#
# In the lingo of this system, cog is an object that receives power from an
# orb. A typical design pattern would be to have a particular network
# relationship being managed by a dedicated cog.
#
#
# // What is the deal with the activity variable in at_turn?
#
# Short answer: it's a mechanism we use to stop your application from running
# the CPU at capacity.
#
# One of the challenges of building an asynchronous application stack is
# handling this problem: how do you stop the event loop from constantly
# cycling through calls to select? If the event loop just cycles continuously,
# it uses up all of that CPU, and then the computer fan comes on. If it's a
# laptop it goes flat rapidly. Users hate that stuff.
#
# The way this system deals with that problem is to track whether there is
# activity on each pass of the event loop. Consider a situation where you're
# downloading something. You want to consume as much data from the network as
# quickly as you can. At these times you want the event look spinning as hard
# as it can. But during the gaps between activity, we want it to hold back.
#
# For each pass of the event loop, if engine thinks there has been activity,
# then it will let the next run of the event loop happen immediately. If there
# hasn't been activity, it gives the event loop a short sleep.
#
# If you're still confused as to what all this is about, please write to me.
# Swapping notes between us might help me to come up with a stronger answer to
# this.
#
#
# // I have several cogs in the same orb. I want them to send messages to one
# // another. I can reference them via the orb, but this does seem a bit
# // hacky. Is there a more elegant approach to do this?
#
# Yes. There's a technique called nearcasting. But at the time of writing it
# hasn't been incorporated to this codebase.
#
# In nearcasting, a cog can update all the other cogs who care with
# purpose-built messages. If you're familiar with Josh Levine's Island
# architecture or the communication systems that modern vehicles run on, you
# may have just lit up and said, "I've always wanted something like this, and
# that sounds awesome." But if you're not, this probably sounded cryptic. I'll
# need to create a demo to give people a chance of groking it.
#
# (If you come to this comment and find that nearcasting still hasn't been
# added, and find you want it, feel free to contact me. I'll be more likely to
# prioritise it over the other integration work I'm doing if I discover that
# there are people who need it. I've been holding off on releasing it so far
# because APIs are hard to change, and I'd like to get the model solid before
# making it public.
#
# Nearcasting enables a powerful development technique for developing
# concurrent systems. The author thinks this technique will be as significant
# for software as the diesel engine was for vehicles. It's coming.
#
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

from solent.eng import engine_new
from solent.eng import QuitEvent
from solent.log import init_logging
from solent.log import log

from collections import deque
import logging
import sys
import time
import traceback
import unittest

def scenario_broadcast_listen(engine):
    net_addr = '127.255.255.255'
    net_port = 50000
    #
    print('''test this with
        echo "Hello" | socat - UDP-DATAGRAM:%s:%s,broadcast
    '''%(net_addr, net_port))
    #
    # We'll gather data to here
    class Cog(object):
        def __init__(self):
            self.sid = engine.open_broadcast_listener(
                addr=net_addr,
                port=net_port,
                cb_sub_recv=self.engine_on_sub_recv)
            self.accumulate = []
        def engine_on_sub_recv(self, cs_sub_recv):
            engine = cs_sub_recv.engine
            sub_sid = cs_sub_recv.sub_sid
            data = cs_sub_recv.data
            #
            self.accumulate.append(data)
        def pull(self):
            s = ''.join( [str(b) for b in self.accumulate] )
            self.accumulate = []
            return s
    #
    # By this point we have a nice reactor-like thing all set
    # up and ready-to-go held within engine_api. All we need to
    # do is to run our while loop, with most of the work to
    # be done for select having been exported to that module.
    class Orb(object):
        def __init__(self):
            self.cog = Cog()
        def at_turn(self, activity):
            data = self.cog.pull()
            if data:
                activity.mark(
                    l='scenario_broadcast_listen',
                    s='found data in cog')
                log('! received [%s] :)'%data)
    orb = Orb()
    engine.add_orb(orb)
    engine.event_loop()

def scenario_broadcast_listen_and_unlisten(engine):
    net_addr = '127.255.255.255'
    net_port = 50000
    #
    print('''
        Testing: you just want it to not crash. (This test doesn't
        process any data it gets from the network while it's connected.)
    ''')
    #
    # We'll gather data to here
    class Cog(object):
        def __init__(self, engine):
            self.engine = engine
            #
            self.sid = engine.open_broadcast_listener(
                addr=net_addr,
                port=net_port,
                cb_sub_recv=self.engine_on_sub_recv)
            self.acc = []
        def close(self):
            self.engine.close_broadcast_listener(self.sid)
        def engine_on_sub_recv(self, cs_sub_recv):
            engine = cs_sub_recv.engine
            sub_sid = cs_sub_recv.sub_sid
            data = cs_sub_recv.data
            #
            self.acc.append(data)
        def pull(self):
            s = ''.join(self.acc)
            self.lst = []
            return s
    class Orb(object):
        def __init__(self, engine):
            self.engine = engine
            #
            self.cogs = [Cog(engine)]
            self.turn_count = 0
        def at_turn(self, activity):
            self.turn_count += 1
            #
            if self.turn_count < 10:
                log('turn %s (cogs active: %s)'%(
                    self.turn_count, len(self.cogs)))
            elif self.turn_count == 10:
                log('test has succeeded or dropped by here.')
            #
            for cog in self.cogs:
                data = cog.pull()
                if data:
                    activity.mark(
                        l='scenario_broadcast_listen_and_unlisten',
                        s='found data in cog')
                    log('received [%s] :)'%data.strip())
                elif self.turn_count >= 6:
                    activity.mark(
                        l='scenario_broadcast_listen_and_unlisten',
                        s='special rule at turn 6.')
                    log('poke note: exit criteria reached [%s]'%(cog.sid))
                    cog.close()
                    self.cogs.remove(cog)
    orb = Orb(engine)
    engine.add_orb(orb)
    #
    # You can use this to print more info about the event loop. This would be
    # useful if you had a flailing event loop and could not work out what was
    # causing the activity.
    engine.debug_eloop_on()
    engine.event_loop()

def scenario_multiple_tcp_servers(engine):
    print('''
        Testing: netcat to one or more of the ports.
    ''')
    #
    class Cog(object):
        def __init__(self, name, engine, addr, port):
            self.name = name
            self.engine = engine
            self.addr = addr
            self.port = port
            # form: (addr, port) : deque containing data
            self.received = {}
            self.server_sid = engine.open_tcp_server(
                addr=addr,
                port=port,
                cb_tcp_connect=self.engine_on_tcp_connect,
                cb_tcp_condrop=self.engine_on_tcp_condrop,
                cb_tcp_recv=self.engine_on_tcp_recv)
        def close(self):
            self.engine.close_tcp_server(self.server_sid)
        def engine_on_tcp_connect(self, cs_tcp_connect):
            engine = cs_tcp_connect.engine
            client_sid = cs_tcp_connect.client_sid
            addr = cs_tcp_connect.addr
            port = cs_tcp_connect.port
            #
            log("connect/%s/%s/%s/%s"%(
                self.name,
                client_sid,
                addr,
                port))
            key = (engine, client_sid)
            self.received[key] = deque()
            engine.send(
                sid=client_sid,
                data='hello, %s:%s!\n'%(addr, port))
        def engine_on_tcp_condrop(self, cs_tcp_condrop):
            engine = cs_tcp_condrop.engine
            client_sid = cs_tcp_condrop.client_sid
            message = cs_tcp_condrop.message
            #
            log("condrop/%s/%s/%s"%(self.name, client_sid, message))
            key = (engine, client_sid)
            del self.received[key]
        def engine_on_tcp_recv(self, cs_tcp_recv):
            engine = cs_tcp_recv.engine
            client_sid = cs_tcp_recv.client_sid
            data = cs_tcp_recv.data
            #
            key = (engine, client_sid)
            self.received[key].append(data)
            engine.send(
                sid=client_sid,
                data='received %s\n'%len(data))
        def at_turn(self, activity):
            pass
    class Orb(object):
        def __init__(self):
            self.cogs = []
        def at_turn(self, activity):
            for cog in self.cogs:
                cog.at_turn(
                    activity=activity)
    #
    details = [ ('x', '127.0.0.1', 4120)
              , ('y', '127.0.0.1', 4121)
              , ('z', '127.0.0.1', 4122)
              ]
    orb = Orb()
    for (name, addr, port) in details:
        cog = Cog(name, engine, addr, port)
        orb.cogs.append(cog)
    engine.add_orb(orb)
    engine.debug_eloop_on()
    engine.event_loop()

def scenario_close_tcp_servers(engine):
    print('''
        Testing: you just want it to not crash.
    ''')
    #
    class Cog(object):
        def __init__(self, name, engine, orb, addr, port, exit_turn):
            self.name = name
            self.engine = engine
            self.orb = orb
            self.addr = addr
            self.port = port
            self.exit_turn = exit_turn
            # form: (addr, port) : deque containing data
            self.received = {}
            self.sid = engine.open_tcp_server(
                addr=addr,
                port=port,
                cb_tcp_connect=self.engine_on_tcp_connect,
                cb_tcp_condrop=self.engine_on_tcp_condrop,
                cb_tcp_recv=self.engine_on_tcp_recv)
        def engine_on_tcp_connect(self, cs_tcp_connect):
            addr = cs_tcp_connect.addr
            port = cs_tcp_connect.port
            engine = cs_tcp_connect.engine
            sid = cs_tcp_connect.client_sid
            #
            log("%s: connect from %s:%s"%(
                self.name,
                addr,
                port))
            key = (engine, sid)
            self.received[key] = deque()
            engine.send(
                sid=sid,
                data='hello, %s:%s!\n'%(addr, port))
        def engine_on_tcp_condrop(self, cs_tcp_condrop):
            engine = cs_tcp_condrop.engine
            client_sid = cs_tcp_condrop.client_sid
            message = cs_tcp_condrop.message
            #
            log("%s: condrop, sid %s"%(
                self.name,
                client_sid))
            key = (engine, client_sid)
            del self.received[key]
        def engine_on_tcp_recv(self, cs_tcp_recv):
            engine = cs_tcp_recv.engine
            client_sid = cs_tcp_recv.client_sid
            data = cs_tcp_recv.data
            #
            key = (engine, client_sid)
            self.received[key].append(data)
            engine.send(
                sid=client_sid,
                data='received %s\n'%len(data))
        def at_turn(self, activity):
            if self.orb.turn_count >= self.exit_turn:
                activity.mark(
                    l='scenario_close_tcp_servers',
                    s='reached turn count')
                log('ordering remove for %s'%self.sid)
                engine.close_tcp_server(self.sid)
                self.orb.cogs.remove(self)
    class Orb(object):
        def __init__(self, engine):
            self.engine = engine
            #
            self.cogs = []
            self.turn_count = 0
        def at_turn(self, activity):
            if self.turn_count <= 30:
                log('turn %s'%self.turn_count)
            elif self.turn_count == 30:
                log('test should have succeeded or dropped by here.')
            #
            for cog in self.cogs:
                cog.at_turn(
                    activity=activity)
            self.turn_count += 1
    orb = Orb(engine)
    details = [ ('x', '127.0.0.1', 4120, 25)
              , ('y', '127.0.0.1', 4121, 10)
              , ('z', '127.0.0.1', 4122, 17)
              ]
    for (name, addr, port, turn_count) in details:
        cog = Cog(name, engine, orb, addr, port, turn_count)
        orb.cogs.append(cog)
    engine.add_orb(orb)
    #
    engine.event_loop()

def scenario_tcp_client_cannot_connect(engine):
    print('''
        test: look for the condrop callback
    ''')
    #
    class Cog(object):
        def __init__(self, name, addr, port):
            self.name = name
            self.addr = addr
            self.port = port
            # form: (addr, port) : deque containing data
            self.received = None
            self.sid = engine.open_tcp_client(
                addr=addr,
                port=port,
                cb_tcp_connect=self.engine_on_tcp_connect,
                cb_tcp_condrop=self.engine_on_tcp_condrop,
                cb_tcp_recv=self.engine_on_tcp_recv)
        def engine_on_tcp_connect(self, cs_tcp_connect):
            engine = cs_tcp_connect.engine
            client_sid = cs_tcp_connect.client_sid
            addr = cs_tcp_connect.addr
            port = cs_tcp_connect.port
            #
            log('connect/%s/%s/%s'%(client_sid, addr, port))
            self.received = deque()
        def engine_on_tcp_condrop(self, cs_tcp_condrop):
            engine = cs_tcp_condrop.engine
            client_sid = cs_tcp_condrop.client_sid
            message = cs_tcp_condrop.message
            #
            self.received = None
            log('** conndrop callback %s'%(client_sid))
        def engine_on_tcp_recv(self, cs_tcp_recv):
            engine = cs_tcp_recv.engine
            client_sid = cs_tcp_recv.client_sid
            data = cs_tcp_recv.data
            #
            self.received.append(data)
        def at_turn(self, activity):
            while self.received:
                log('client|%s'%(self.received.popleft().strip()))
    class Orb(object):
        def __init__(self):
            self.cogs = []
        def at_turn(self, activity):
            for cog in self.cogs:
                cog.at_turn(
                    activity=activity)
    orb = Orb()
    engine.add_orb(orb)
    #
    details = { 'p': ('localhost', 1233)
              }
    for (name, (addr, port)) in details.items():
        cog = Cog(name, addr, port)
        orb.cogs.append(cog)
    #
    engine.event_loop()

def scenario_tcp_client_mixed_scenarios(engine):
    #
    # This test demonstrates TCP connection behaviour to
    #   (1) a server which is always up (ssh port on a webserver I run)
    #   (2) a port which is not running (localhost:1234)
    #
    # The print statement below shows hos the user can run up a netcat server
    # on localhost if they want to try that.
    #
    print('''
        If you want to run a netcat server on localhost :1234, you can do this:
          nc -l -p 1234
        (This can be useful to verify that a condrop gets called even
        when the disconnect is initiated from this side.)
    ''')
    #
    class Cog(object):
        def __init__(self, name, engine, orb, addr, port, close_turn):
            self.name = name
            self.engine = engine
            self.orb = orb
            self.addr = addr
            self.port = port
            self.close_turn = close_turn
            #
            self.sid = engine.open_tcp_client(
                addr=addr,
                port=port,
                cb_tcp_connect=self.engine_on_tcp_connect,
                cb_tcp_condrop=self.engine_on_tcp_condrop,
                cb_tcp_recv=self.engine_on_tcp_recv)
            self.b_dropped = False
            # form: (addr, port) : deque containing data
            self.received = None
        def engine_on_tcp_connect(self, cs_tcp_connect):
            engine = cs_tcp_connect.engine
            client_sid = cs_tcp_connect.client_sid
            addr = cs_tcp_connect.addr
            port = cs_tcp_connect.port
            #
            log('connect/%s/%s/%s'%(client_sid, addr, port))
            self.received = deque()
            self.b_dropped = False
        def engine_on_tcp_condrop(self, cs_tcp_condrop):
            engine = cs_tcp_condrop.engine
            client_sid = cs_tcp_condrop.client_sid
            message = cs_tcp_condrop.message
            #
            log("condrop/%s/%s/%s"%(self.name, client_sid, message))
            self.received = None
            self.b_dropped = True
        def engine_on_tcp_recv(self, cs_tcp_recv):
            engine = cs_tcp_recv.engine
            client_sid = cs_tcp_recv.client_sid
            data = cs_tcp_recv.data
            #
            self.received.append(data)
        def at_turn(self, activity):
            if self.b_dropped:
                return
            while self.received:
                activity.mark(
                    l='scenario_tcp_client_mixed_scenarios',
                    s='received data from net')
                log('client|%s'%(self.received.popleft().strip()))
            if self.orb.turn_count == self.close_turn:
                log('closing %s/%s on turn %s'%(
                    self.name, self.sid, self.orb.turn_count))
                activity.mark(
                    l='scenario_tcp_client_mixed_scenarios',
                    s='reached turn count')
                engine.close_tcp_client(self.sid)
                self.orb.cogs.remove(self)
    class Orb(object):
        def __init__(self):
            self.cogs = []
            self.turn_count = 0
        def at_turn(self, activity):
            for cog in self.cogs:
                cog.at_turn(
                    activity=activity)
            self.turn_count += 1
    #
    # ports we will create
    details = { 'p': ('songseed.org', 22, 7)
              , 'q': ('localhost', 1234, 12)
              }
    orb = Orb()
    for (name, (addr, port, close_turn)) in details.items():
        orb.cogs.append(
            Cog(
                name=name,
                engine=engine,
                orb=orb,
                addr=addr,
                port=port,
                close_turn=close_turn))
    engine.add_orb(orb)
    #
    # here we go!
    engine.event_loop()

def scenario_broadcast_post(engine):
    addr = '127.255.255.255'
    port = 50000
    log('''You can watch this data with the qd_listen tool:
        python3 -m solent.tools.qd_listen %s %s'''%(addr, port))
    #
    class Cog(object):
        def __init__(self, engine, orb, addr, port):
            self.engine = engine
            self.orb = orb
            #
            self.sid = engine.open_broadcast_sender(
                addr=addr,
                port=port)
            self.last_t = time.time()
        def at_turn(self, activity):
            t = time.time()
            if t - self.last_t > 2:
                activity.mark(
                    l='scenario_broadcast_post',
                    s='two seconds passed')
                self.last_t = t
                self.engine.send(
                    sid=self.sid,
                    data='from poke [%s]'%t)
    class Orb(object):
        def __init__(self, engine):
            self.engine = engine
            #
            self.cogs = []
        def at_turn(self, activity):
            for cog in self.cogs:
                cog.at_turn(
                    activity=activity)
    orb = Orb(engine)
    orb.cogs.append(Cog(engine, orb, addr, port))
    engine.add_orb(orb)
    engine.event_loop()

def scenario_broadcast_post_with_del(engine):
    addr = '127.255.255.255'
    port = 50000
    log('to test this, qd %s %s'%(addr, port))
    #
    class Cog(object):
        def __init__(self, engine, orb, addr, port):
            self.engine = engine
            self.orb = orb
            self.addr = addr
            self.port = port
            #
            self.sid = engine.open_broadcast_sender(
                addr=addr,
                port=port)
            self.last_t = time.time()
            self.count_turns = 0
        def at_turn(self, activity):
            t = time.time()
            if t - self.last_t > 1:
                activity.mark(
                    l='scenario_broadcast_post_with_del',
                    s='time interval')
                log('sending to %s:%s'%(self.addr, self.port))
                engine.send(
                    sid=self.sid,
                    data='from poke [%s]'%(t))
                self.last_t = t
            self.count_turns += 1
            if self.count_turns == 20:
                activity.mark(
                    l='scenario_broadcast_post_with_del',
                    s='count interval')
                log('cog is self-closing')
                engine.close_broadcast_sender(self.sid)
                self.orb.cogs.remove(self)
    class Orb(object):
        def __init__(self, engine):
            self.engine = engine
            #
            self.cogs = []
        def at_turn(self, activity):
            for cog in self.cogs:
                cog.at_turn(
                    activity=activity)
    orb = Orb(engine)
    engine.add_orb(orb)
    cog = Cog(engine, orb, addr, port)
    orb.cogs.append(cog)
    engine.event_loop()

def main():
    init_logging()

    engine = engine_new(
        mtu=1492)
    try:
        #
        # Comment these in or out as you want to test scenarios.
        #
        scenario_broadcast_listen(engine)
        #scenario_broadcast_listen_and_unlisten(engine)
        #scenario_multiple_tcp_servers(engine)
        #scenario_close_tcp_servers(engine)
        #scenario_tcp_client_cannot_connect(engine)
        #scenario_tcp_client_mixed_scenarios(engine)
        #scenario_broadcast_post(engine)
        #scenario_broadcast_post_with_del(engine)
        pass
    except KeyboardInterrupt:
        pass
    except:
        traceback.print_exc()
    finally:
        engine.close()

if __name__ == '__main__':
    main()

