#!/usr/bin/python -B
#
# Scenarios.
#
# Welcome. This class intends to be the easy-to-use path for users who want
# to use eng.
#
# xxx todo: migrate to https://github.com/cratuki/solent/wiki
#
#
# --------------------------------------------------------
#   faq
# --------------------------------------------------------
#
# // What is the purpose of solent.eng?
#
# To wrap the Berkeley sockets API with a much friendlier interface that makes
# it straightforward to create an event loop around managed sockets.
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
# Think of the engine a bit like the engine of a car. It powers a crankshaft.
# Anything in the car that needs to be powered by the engine hangs off the
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
# // I have several cogs in the same orb. I want them to send messages to one
# // another. I can reference them via the orb, but this does seem a bit
# // hacky. Is there a more elegant approach to do this?
#
# Yes. Use nearcasting for this.
#
# In nearcasting, a cog can update all the other cogs who care with
# message broadcasts. This nearcasting idea is really the essence of this
# system.
#
# There's an example scenario below. One actor nearcasts, all the others get
# the message.
#
# solent.gruel.server shows a larger example.
#
#
# --------------------------------------------------------
#   license
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

from solent import SolentQuitException
from solent.eng import engine_new
from solent.eng import orb_new
from solent.eng import nearcast_schema_new
from solent.eng import QuitEvent
from solent.log import init_logging
from solent.log import log
from solent.util import line_finder_new

from collections import deque
import logging
import sys
import time
import traceback
import unittest

def scenario_basic_nearcast_example(engine):
    '''
    // What's happening here?

    We define a nearcast schema. The cogs can use this to communicate between
    one another. In this schema, there is a single type of message defined,
    the nearcast_note. It has two fields.

    CogSender will be instantiated. It will count turns of the event
    loop. On turn #3 it nearcasts.

    CogPrint will be instantiated. It has a method that watches for messages
    of type nearcast_note, and then prints them out.

    CogQuitter will be instantiated. It counts turns, and quits a while
    longer than the other activity.

    '''
    # this is a dsl for defining nearcasts
    i_nearcast = '''
        i message h
        i field h

        message nearcast_note
            field field_a
            field field_b
    '''
    #
    class CogSender:
        def __init__(self, cog_h, orb, engine):
            self.cog_h = cog_h
            self.orb = orb
            self.engine = engine
            #
            self.turn_counter = 0
        def at_turn(self, activity):
            self.turn_counter += 1
            if self.turn_counter == 3:
                activity.mark(
                    l=self,
                    s="reached the important turn")
                self.orb.nearcast(
                    cog=self,
                    message_h='nearcast_note',
                    field_a='text in a',
                    field_b='text in b')
                log('%s sent nearcast note'%(self.cog_h))
    class CogPrinter:
        def __init__(self, cog_h, orb, engine):
            self.cog_h = cog_h
            self.orb = orb
            self.engine = engine
        def on_nearcast_note(self, field_a, field_b):
            log('%s received nearcast_note [%s] [%s]'%(
                self.cog_h, field_a, field_b))
    class CogQuitter:
        def __init__(self, cog_h, orb, engine):
            self.cog_h = cog_h
            self.orb = orb
            self.engine = engine
            #
            self.turn_counter = 0
        def at_turn(self, activity):
            self.turn_counter += 1
            if self.turn_counter == 8:
                activity.mark(
                    l=self,
                    s='last turn, quitting')
                log('quitting')
                raise SolentQuitException()
    #
    nearcast_schema = nearcast_schema_new(
        i_nearcast=i_nearcast)
    orb = engine.init_orb(
        orb_h=__name__,
        nearcast_schema=nearcast_schema)
    orb.init_cog(CogSender)
    orb.init_cog(CogPrinter)
    orb.init_cog(CogQuitter)
    engine.event_loop()

def scenario_broadcast_listen(engine):
    net_addr = '127.255.255.255'
    net_port = 50000
    print('''test this with
        echo "Hello" | socat - UDP-DATAGRAM:%s:%s,broadcast
    '''%(net_addr, net_port))
    #
    i_nearcast = '''
        i message h
        i field h

        message start_listener
            field ip
            field port

        message stop_listener

        message received_from_network
            field data
    '''
    #
    # This class provides broadcast listen functionality. It's not tied
    # the the nearcast schema. It just exposes a standard application
    # interface.
    class SpinBroadcastListener:
        def __init__(self, engine, cb_on_line):
            self.engine = engine
            self.cb_on_line = cb_on_line
            #
            self.sid = None
            self.line_finder = line_finder_new(
                cb_line=self.cb_on_line)
        def start(self, ip, port):
            self.sid = engine.open_broadcast_listener(
                addr=net_addr,
                port=net_port,
                cb_sub_recv=self._net_on_line)
        def stop(self):
            self.line_finder.clear()
        def _net_on_line(self, cs_sub_recv):
            engine = cs_sub_recv.engine
            sub_sid = cs_sub_recv.sub_sid
            data = cs_sub_recv.data
            #
            self.line_finder.accept_bytes(
                barr=data)
    #
    # We'll gather data to here
    class CogContainsSpin:
        def __init__(self, cog_h, orb, engine):
            self.cog_h = cog_h
            self.orb = orb
            self.engine = engine
            #
            self.spin_broadcast_listener = SpinBroadcastListener(
                engine=engine,
                cb_on_line=self._broadcast_on_line)
        def _broadcast_on_line(self, line):
            self.orb.nearcast(
                cog=self,
                message_h='received_from_network',
                data=line)
        def on_start_listener(self, ip, port):
            self.spin_broadcast_listener.start(
                ip=ip,
                port=port)
        def on_stop_listener(self):
            self.spin_broadcast_listener.stop()
    #
    #
    class CogPrinter:
        def __init__(self, cog_h, orb, engine):
            self.cog_h = cog_h
            self.orb = orb
            self.engine = engine
        def on_received_from_network(self, data):
            log('! received [%s] :)'%(data))
    #
    # This manages scheduling.
    class CogEvents:
        def __init__(self, cog_h, orb, engine):
            self.cog_h = cog_h
            self.orb = orb
            self.engine = engine
            #
            self.turn_counter = 0
        def at_turn(self, activity):
            self.turn_counter += 1
            if self.turn_counter == 2:
                activity.mark(
                    l=self,
                    s='starting listener')
                self.orb.nearcast(
                    cog=self,
                    message_h='start_listener',
                    ip=net_addr,
                    port=net_port)
    #
    orb = engine.init_orb(
        orb_h=__name__,
        nearcast_schema=nearcast_schema_new(
            i_nearcast=i_nearcast))
    orb.init_cog(CogContainsSpin)
    orb.init_cog(CogPrinter)
    orb.init_cog(CogEvents)
    #
    # You can use this to print more info about the event loop. This would be
    # useful if you had a flailing event loop and could not work out what was
    # causing the activity.
    engine.debug_eloop_on()
    engine.event_loop()

def scenario_broadcast_listen_and_unlisten(engine):
    net_addr = '127.255.255.255'
    net_port = 50000
    print('''test this with
        echo "Hello" | socat - UDP-DATAGRAM:%s:%s,broadcast
    '''%(net_addr, net_port))
    #
    i_nearcast = '''
        i message h
        i field h

        message start_listener
            field ip
            field port

        message stop_listener

        message received_from_network
            field data
    '''
    #
    # This class provides broadcast listen functionality. It's not tied
    # the the nearcast schema. It just exposes a standard application
    # interface.
    class SpinBroadcastListener:
        def __init__(self, engine, cb_on_line):
            self.engine = engine
            self.cb_on_line = cb_on_line
            #
            self.sid = None
            self.line_finder = line_finder_new(
                cb_line=self.cb_on_line)
        def start(self, ip, port):
            self.sid = engine.open_broadcast_listener(
                addr=net_addr,
                port=net_port,
                cb_sub_recv=self._net_on_line)
        def stop(self):
            self.line_finder.clear()
            self.engine.close_broadcast_listener(
                sid=self.sid)
        def _net_on_line(self, cs_sub_recv):
            engine = cs_sub_recv.engine
            sub_sid = cs_sub_recv.sub_sid
            data = cs_sub_recv.data
            #
            self.line_finder.accept_bytes(
                barr=data)
    #
    # We'll gather data to here
    class CogContainsSpin:
        def __init__(self, cog_h, orb, engine):
            self.cog_h = cog_h
            self.orb = orb
            self.engine = engine
            #
            self.spin_broadcast_listener = SpinBroadcastListener(
                engine=engine,
                cb_on_line=self._broadcast_on_line)
        def _broadcast_on_line(self, line):
            self.orb.nearcast(
                cog=self,
                message_h='received_from_network',
                data=line)
        def on_start_listener(self, ip, port):
            self.spin_broadcast_listener.start(
                ip=ip,
                port=port)
        def on_stop_listener(self):
            self.spin_broadcast_listener.stop()
    #
    #
    class CogPrinter:
        def __init__(self, cog_h, orb, engine):
            self.cog_h = cog_h
            self.orb = orb
            self.engine = engine
        def on_received_from_network(self, data):
            log('! received [%s] :)'%(data))
    #
    # This manages scheduling.
    class CogEvents:
        def __init__(self, cog_h, orb, engine):
            self.cog_h = cog_h
            self.orb = orb
            self.engine = engine
            #
            self.turn_counter = 0
        def at_turn(self, activity):
            self.turn_counter += 1
            if self.turn_counter == 2:
                activity.mark(
                    l=self,
                    s='starting listener')
                self.orb.nearcast(
                    cog=self,
                    message_h='start_listener',
                    ip=net_addr,
                    port=net_port)
            elif self.turn_counter == 20:
                activity.mark(
                    l=self,
                    s='stopping listener')
                self.orb.nearcast(
                    cog=self,
                    message_h='stop_listener')
    nearcast_schema = nearcast_schema_new(
        i_nearcast=i_nearcast)
    orb = engine.init_orb(
        orb_h=__name__,
        nearcast_schema=nearcast_schema)
    # We are going to create a snoop here. This one logs nearcast messages as
    # they happen.
    orb.add_log_snoop()
    orb.init_cog(CogContainsSpin)
    orb.init_cog(CogPrinter)
    orb.init_cog(CogEvents)
    #
    # You can use this to print more info about the event loop. This would be
    # useful if you had a flailing event loop and could not work out what was
    # causing the activity.
    engine.debug_eloop_on()
    engine.event_loop()

class SpinTcpEchoServer:
    def __init__(self, spin_h, engine):
        self.spin_h = spin_h
        self.engine = engine
        #
        self.b_active = False
        self.server_ip = None
        self.server_port = None
        self.server_sid = None
        self.client_sid = None
    def start(self, spin_h, ip, port):
        self.b_active = True
        self.server_ip = ip
        self.server_port = port
        self._start_server()
        log('** started %s %s:%s'%(self.spin_h, ip, port))
    def stop(self):
        self._boot_any_client()
        self._close_any_server()
        self.b_active = False
        log('** stopped %s'%(self.spin_h))
    def at_turn(self, activity):
        if self.b_active:
            # restart the server after a client disconnect
            if self.server_sid == None and self.client_sid == None:
                activity.mark(
                    l=self,
                    s='starting server')
                self._start_server()
    def _start_server(self):
        self.server_sid = self.engine.open_tcp_server(
            addr=self.server_ip,
            port=self.server_port,
            cb_tcp_connect=self.engine_on_tcp_connect,
            cb_tcp_condrop=self.engine_on_tcp_condrop,
            cb_tcp_recv=self.engine_on_tcp_recv)
    def _close_any_server(self):
        if self.server_sid == None:
            return
        self.engine.close_tcp_client(
            sid=self.server_sid)
        self.server_sid = None
    def _boot_any_client(self):
        if self.client_sid == None:
            return
        self.engine.close_tcp_client(
            sid=self.client_sid)
        self.client_sid = None
    def engine_on_tcp_connect(self, cs_tcp_connect):
        engine = cs_tcp_connect.engine
        client_sid = cs_tcp_connect.client_sid
        addr = cs_tcp_connect.addr
        port = cs_tcp_connect.port
        #
        self.client_sid = client_sid
        self._close_any_server()
    def engine_on_tcp_condrop(self, cs_tcp_condrop):
        engine = cs_tcp_condrop.engine
        client_sid = cs_tcp_condrop.client_sid
        message = cs_tcp_condrop.message
        #
        self.client_sid = None
    def engine_on_tcp_recv(self, cs_tcp_recv):
        engine = cs_tcp_recv.engine
        client_sid = cs_tcp_recv.client_sid
        data = cs_tcp_recv.data
        #
        payload = bytes(
            source='(echo from %s) [%s]\n'%(self.spin_h, data),
            encoding='utf8')
        engine.send(
            sid=client_sid,
            payload=payload)

def scenario_multiple_tcp_servers(engine):
    print('''
        Testing: netcat to one or more of the ports.
    ''')
    i_nearcast = '''
        i message h
        i field h

        message start_echo_server
            field spin_h
            field ip
            field port

        message stop_echo_server
            field spin_h
    '''
    #
    class CogServerContainer:
        def __init__(self, cog_h, orb, engine):
            self.cog_h = cog_h
            self.orb = orb
            self.engine = engine
            #
            self.servers = {}
        def on_start_echo_server(self, spin_h, ip, port):
            spin_tcp_echo_server = SpinTcpEchoServer(
                spin_h=spin_h,
                engine=engine)
            self.servers[spin_h] = spin_tcp_echo_server
            spin_tcp_echo_server.start(
                spin_h=spin_h,
                ip=ip,
                port=port)
        def on_stop_echo_server(self, spin_h):
            self.servers[spin_h].stop()
            del self.servers[spin_h]
        def at_turn(self, activity):
            for server in self.servers.values():
                server.at_turn(
                    activity=activity)
    class CogEvents:
        def __init__(self, cog_h, orb, engine):
            self.cog_h = cog_h
            self.orb = orb
            self.engine = engine
            self.turn_counter = 0
        def at_turn(self, activity):
            schedule = { 3: ('x', '127.0.0.1', 4120)
                       , 5: ('y', '127.0.0.1', 4121)
                       , 8: ('z', '127.0.0.1', 4122)
                       }
            self.turn_counter += 1
            if self.turn_counter in schedule:
                (spin_h, ip, port) = schedule[self.turn_counter]
                activity.mark(
                    l=self,
                    s='starting server %s'%spin_h)
                self.orb.nearcast(
                    cog=self,
                    message_h='start_echo_server',
                    spin_h=spin_h,
                    ip=ip,
                    port=port)
    #
    nearcast_schema = nearcast_schema_new(
        i_nearcast=i_nearcast)
    orb = engine.init_orb(
        orb_h=__name__,
        nearcast_schema=nearcast_schema)
    orb.init_cog(CogEvents)
    orb.init_cog(CogServerContainer)
    engine.event_loop()

def scenario_close_tcp_servers(engine):
    print('''
        Testing: you just want it to not crash.
    ''')
    #
    i_nearcast = '''
        i message h
        i field h

        message start_echo_server
            field spin_h
            field ip
            field port

        message stop_echo_server
            field spin_h
    '''
    #
    class CogServerContainer:
        def __init__(self, cog_h, orb, engine):
            self.cog_h = cog_h
            self.orb = orb
            self.engine = engine
            #
            self.servers = {}
        def on_start_echo_server(self, spin_h, ip, port):
            spin_tcp_echo_server = SpinTcpEchoServer(
                spin_h=spin_h,
                engine=engine)
            self.servers[spin_h] = spin_tcp_echo_server
            spin_tcp_echo_server.start(
                spin_h=spin_h,
                ip=ip,
                port=port)
        def on_stop_echo_server(self, spin_h):
            self.servers[spin_h].stop()
            del self.servers[spin_h]
        def at_turn(self, activity):
            for server in self.servers.values():
                server.at_turn(
                    activity=activity)
    class CogEvents:
        def __init__(self, cog_h, orb, engine):
            self.cog_h = cog_h
            self.orb = orb
            self.engine = engine
            self.turn_counter = 0
        def at_turn(self, activity):
            open_schedule = {
                3: ('x', '127.0.0.1', 4120),
                5: ('y', '127.0.0.1', 4121),
                8: ('z', '127.0.0.1', 4122)}
            close_schedule = {
                10: 'z',
                15: 'y',
                30: 'x'}
            self.turn_counter += 1
            if self.turn_counter in open_schedule:
                (spin_h, ip, port) = open_schedule[self.turn_counter]
                activity.mark(
                    l=self,
                    s='starting server %s'%spin_h)
                self.orb.nearcast(
                    cog=self,
                    message_h='start_echo_server',
                    spin_h=spin_h,
                    ip=ip,
                    port=port)
            if self.turn_counter in close_schedule:
                spin_h = close_schedule[self.turn_counter]
                activity.mark(
                    l=self,
                    s='stopping server %s'%spin_h)
                self.orb.nearcast(
                    cog=self,
                    message_h='stop_echo_server',
                    spin_h=spin_h)
            if self.turn_counter == 25:
                raise SolentQuitException()
    #
    nearcast_schema = nearcast_schema_new(
        i_nearcast=i_nearcast)
    orb = engine.init_orb(
        orb_h=__name__,
        nearcast_schema=nearcast_schema)
    orb.init_cog(CogEvents)
    orb.init_cog(CogServerContainer)
    try:
        engine.event_loop()
    except SolentQuitException:
        pass

def scenario_tcp_client_cannot_connect(engine):
    #
    # This scenario is still using an old code style where (1) we have a
    # custom orb; (2) there is network functionality in the cog, rather than
    # in a separate spin class and (3) it predates nearcasting. This needs to
    # be updated. It's useful for testing, and does show how to open a client
    # connection, but is not a good style example
    #
    print('''
        test: look for the condrop callback
    ''')
    #
    class Cog:
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
    class Orb:
        def __init__(self):
            self.cogs = []
        def at_turn(self, activity):
            for cog in self.cogs:
                cog.at_turn(
                    activity=activity)
    orb = Orb()
    engine.add_orb(
        orb_h=__name__,
        orb=orb)
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
    # This scenario is still using an old code style where we put network
    # logic in cogs (rather than spins), and it predates nearcasting. It's
    # useful for testing but not a good style example.
    #
    print('''
        If you want to run a netcat server on localhost :1234, you can do this:
          nc -l -p 1234
        (This can be useful to verify that a condrop gets called even
        when the disconnect is initiated from this side.)
    ''')
    #
    class Cog:
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
    class Orb:
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
    engine.add_orb(
        orb_h=__name__,
        orb=orb)
    #
    # here we go!
    engine.event_loop()

def scenario_broadcast_post(engine):
    #
    # This is not a good style example. Predates nearcasting.
    #
    addr = '127.255.255.255'
    port = 50000
    log('''You can watch this data with the qd_listen tool:
        python3 -m solent.tools.qd_listen %s %s'''%(addr, port))
    #
    class Cog:
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
                payload = bytes(
                    source='from poke [%s]'%t,
                    encoding='utf8')
                self.engine.send(
                    sid=self.sid,
                    payload=payload)
    class Orb:
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
    engine.add_orb(
        orb_h=__name__,
        orb=orb)
    engine.event_loop()

def scenario_broadcast_post_with_del(engine):
    #
    # This is not a good style example. Predates nearcasting.
    #
    addr = '127.255.255.255'
    port = 50000
    log('to test this, qd %s %s'%(addr, port))
    #
    class Cog:
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
                payload = bytes(
                    source='from poke [%s]'%(t),
                    encoding='utf8')
                engine.send(
                    sid=self.sid,
                    payload=payload)
                self.last_t = t
            self.count_turns += 1
            if self.count_turns == 20:
                activity.mark(
                    l='scenario_broadcast_post_with_del',
                    s='count interval')
                log('cog is self-closing')
                engine.close_broadcast_sender(self.sid)
                self.orb.cogs.remove(self)
    class Orb:
        def __init__(self, engine):
            self.engine = engine
            #
            self.cogs = []
        def at_turn(self, activity):
            for cog in self.cogs:
                cog.at_turn(
                    activity=activity)
    orb = Orb(engine)
    engine.add_orb(
        orb_h=__name__,
        orb=orb)
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
        #scenario_basic_nearcast_example(engine)
        #scenario_broadcast_listen(engine)
        #scenario_broadcast_listen_and_unlisten(engine)
        #scenario_multiple_tcp_servers(engine)
        #scenario_close_tcp_servers(engine)
        #scenario_tcp_client_cannot_connect(engine)
        #scenario_tcp_client_mixed_scenarios(engine)
        #scenario_broadcast_post(engine)
        scenario_broadcast_post_with_del(engine)
        pass
    except KeyboardInterrupt:
        pass
    except SolentQuitException:
        pass
    except:
        traceback.print_exc()
    finally:
        engine.close()

def scenarios_empty():
    # use this in testing
    pass

if __name__ == '__main__':
    main()

