#!/usr/bin/python -B
#
# Scenarios.
#
# Welcome. This class intends to be the easy-to-use path for users who want
# to use eng.
#
#
# --------------------------------------------------------
#   faq
# --------------------------------------------------------
#
# // What is the purpose of solent.eng?
#
# To create an easy-to-use asynchronous event loop. Part of this involves
# wrapping the Berkeley sockets API with a friendlier interface. This new
# interface is easier to work when when you are building systems composed
# of small actors.
#
#
# // How do I use eng?
#
# Find a scenario function below that matches what you are trying to do. These
# scenarios have dual uses. They're useful for eng developers to test
# scenarios when they are working on the system. And they're useful for
# application developers to learn-by-example.
#
#
# // What does sid mean? What is a sid?
#
# It's a reference to an engine-managed socket. In order to facade the
# Berkeley sockets API with a friendlier interface, it was necessary to
# completely encase supported socket-access scenarios within the engine. Sid
# is a reference to an engine-managed socket.
#
#
# // What's the deal with these cs objects I get in callbacks?
#
# See the header of cs.py for an explanation of these, and the pydoc of the
# classes in that module for individual explanations.
#
#
# // What is a spin?
#
# A spin is an actor that you can add to the engine. The initiative of the
# engine gets transferred into business logic via spins, or via orbs (and orb
# is just a special kind of spin that happens to be bundled with solent).
# Spins gets regular turns.
#
#
# // What is an orb?
#
# Imagine you had multiple spins attached to an engine. There would be no
# obvious way for them to communicate with one another.
#
# The solution to this is an orb. An orb is a spin that has a messaging layer
# inside it called a nearcast. Whenever a message is nearcast, any cog
# attached to that orb can receive the message. If a message called
# 'define_symbol' was nearcast, any attached orb with a method called
# 'on_define_symbol' would be sent a copy of the message.
#
# Typically, an orb will be a container for a set of related services. (cogs,
# see below)
#
# Several scenarios below assemble orbs and cogs to address a problem.
#
#
# // What is a cog?
#
# A cog is a simple unit of business logic. It is instantiated via a call
# to the orb it will be attached to. It has the opportunity to send messages
# to its orb's nearcast (e.g. self.nearcast.define_symbol()) and it can
# receive any message sent to its orb's nearcast by defining a method
# referring to the message name (e.g. on_define_symbol).
#
# A handy pattern to use: instantiate spins within cogs. The spins can be
# stand-alone objects. Cogs act as the bridge between the messaging schema
# of the current application and the API of these standalone spins.
#
#
# // I have several cogs in the same orb. I want them to send messages to one
# // another. I can reference them via the orb, but this does seem a bit
# // hacky. Is there a more elegant approach to do this?
#
# Yes. Use nearcasting for this.
#
# There's an example scenario below. One actor nearcasts, all the others get
# the message.
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
    orb = engine.init_orb(
        spin_h=__name__,
        i_nearcast=i_nearcast)
    orb.init_cog(CogSender)
    orb.init_cog(CogPrinter)
    orb.init_cog(CogQuitter)
    engine.event_loop()

#
# This class provides broadcast listen functionality. It's easy to
# embed this within a cog.
class BroadcastListener:
    def __init__(self, engine, addr, port, cb_on_line):
        self.engine = engine
        self.addr = addr
        self.port = port
        self.cb_on_line = cb_on_line
        #
        self.sub_sid = None
        self.line_finder = line_finder_new(
            cb_line=self.cb_on_line)
    def start(self, ip, port):
        self.engine.open_sub(
            addr=self.addr,
            port=self.port,
            cb_sub_start=self._engine_on_sub_start,
            cb_sub_stop=self._engine_on_sub_stop,
            cb_sub_recv=self._engine_on_sub_recv)
    def stop(self):
        self.engine.close_sub(
            sub_sid=self.sub_sid)
    def _engine_on_sub_start(self, cs_sub_start):
        engine = cs_sub_start.engine
        sub_sid = cs_sub_start.sub_sid
        addr = cs_sub_start.addr
        port = cs_sub_start.port
        #
        log('sub %s started %s:%s'%(sub_sid, addr, port))
        #
        self.sub_sid = sub_sid
        self.line_finder.clear()
    def _engine_on_sub_stop(self, cs_sub_stop):
        engine = cs_sub_stop.engine
        sub_sid = cs_sub_stop.sub_sid
        message = cs_sub_stop.message
        #
        log('sub stopped %s'%sub_sid)
        #
        self.sub_sid = None
        self.line_finder.clear()
    def _engine_on_sub_recv(self, cs_sub_recv):
        engine = cs_sub_recv.engine
        sub_sid = cs_sub_recv.sub_sid
        bb = cs_sub_recv.bb
        #
        log('sub recv (len %s)'%(len(bb)))
        #
        self.line_finder.accept_bytes(
            barr=bb)

def scenario_sub_simple(engine):
    net_addr = '127.255.255.255'
    net_port = 50000
    print('''test this with
        echo "Hello" | socat - UDP-DATAGRAM:%s:%s,broadcast
    Or
        python3 -m solent.tools.qd_poll 127.255.255.255 50000
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
            field bb
    '''
    class CogBroadcastListener:
        def __init__(self, cog_h, orb, engine):
            self.cog_h = cog_h
            self.orb = orb
            self.engine = engine
            #
            self.broadcast_listener = BroadcastListener(
                engine=engine,
                addr=net_addr,
                port=net_port,
                cb_on_line=self._broadcast_on_line)
        def _broadcast_on_line(self, line):
            self.orb.nearcast(
                cog=self,
                message_h='received_from_network',
                bb=line)
        def on_start_listener(self, ip, port):
            self.broadcast_listener.start(
                ip=ip,
                port=port)
        def on_stop_listener(self):
            self.broadcast_listener.stop()
    class CogEvents:
        'This manages scheduling.'
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
    class CogPrinter:
        def __init__(self, cog_h, orb, engine):
            self.cog_h = cog_h
            self.orb = orb
            self.engine = engine
        def on_received_from_network(self, bb):
            log('! received [%s] :)'%(bb))
    #
    orb = engine.init_orb(
        spin_h=__name__,
        i_nearcast=i_nearcast)
    orb.init_cog(CogEvents)
    orb.init_cog(CogBroadcastListener)
    orb.init_cog(CogPrinter)
    #
    # You can use this to print more info about the event loop. This would be
    # useful if you had a flailing event loop and could not work out what was
    # causing the activity.
    engine.debug_eloop_on()
    engine.event_loop()

def scenario_sub_listen_and_unlisten(engine):
    net_addr = '127.255.255.255'
    net_port = 50000
    print('''test this with
        echo "Hello" | socat - UDP-DATAGRAM:%s:%s,broadcast
    Or
        python3 -m solent.tools.qd_poll 127.255.255.255 50000
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
            field bb
    '''
    class CogEvents:
        'This manages scheduling.'
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
    class CogBroadcastListener:
        def __init__(self, cog_h, orb, engine):
            self.cog_h = cog_h
            self.orb = orb
            self.engine = engine
            #
            self.broadcast_listener = BroadcastListener(
                engine=engine,
                addr=net_addr,
                port=net_port,
                cb_on_line=self._broadcast_on_line)
        def on_start_listener(self, ip, port):
            self.broadcast_listener.start(
                ip=ip,
                port=port)
        def on_stop_listener(self):
            self.broadcast_listener.stop()
        def _broadcast_on_line(self, line):
            self.orb.nearcast(
                cog=self,
                message_h='received_from_network',
                bb=line)
    class CogPrinter:
        def __init__(self, cog_h, orb, engine):
            self.cog_h = cog_h
            self.orb = orb
            self.engine = engine
        def on_received_from_network(self, bb):
            log('! received [%s] :)'%(bb))
    orb = engine.init_orb(
        spin_h=__name__,
        i_nearcast=i_nearcast)
    # We are going to create a snoop here. This one logs nearcast messages as
    # they happen.
    orb.add_log_snoop()
    orb.init_cog(CogEvents)
    orb.init_cog(CogBroadcastListener)
    orb.init_cog(CogPrinter)
    #
    # You can use this to print more info about the event loop. This would be
    # useful if you had a flailing event loop and could not work out what was
    # causing the activity.
    engine.debug_eloop_on()
    engine.event_loop()

class SimpleEchoServer:
    def __init__(self, spin_h, engine):
        self.spin_h = spin_h
        self.engine = engine
        #
        self.b_active = False
        self.server_ip = None
        self.server_port = None
        self.server_sid = None
        self.accept_sid = None
    def at_turn(self, activity):
        pass
    def at_close(self):
        self._close_everything()
    #
    def start(self, ip, port):
        self.b_active = True
        self.server_ip = ip
        self.server_port = port
        #
        self._start_server()
    def stop(self):
        self._close_everything()
    #
    def _close_everything(self):
        log('** /server/close_everything')
        self.b_active = False
        self._boot_any_client()
        self._stop_any_server()
    def _start_server(self):
        self.engine.open_tcp_server(
            addr=self.server_ip,
            port=self.server_port,
            cb_tcp_server_start=self.engine_on_tcp_server_start,
            cb_tcp_server_stop=self.engine_on_tcp_server_stop,
            cb_tcp_accept_connect=self.engine_on_tcp_accept_connect,
            cb_tcp_accept_condrop=self.engine_on_tcp_accept_condrop,
            cb_tcp_accept_recv=self.engine_on_tcp_accept_recv)
    def _boot_any_client(self):
        if self.accept_sid == None:
            return
        self.engine.close_tcp_client(
            client_sid=self.accept_sid)
        self.accept_sid = None
    def _stop_any_server(self):
        if self.server_sid == None:
            return
        self.engine.close_tcp_server(
            server_sid=self.server_sid)
    def engine_on_tcp_accept_connect(self, cs_tcp_accept_connect):
        engine = cs_tcp_accept_connect.engine
        server_sid = cs_tcp_accept_connect.server_sid
        accept_sid = cs_tcp_accept_connect.accept_sid
        client_addr = cs_tcp_accept_connect.client_addr
        client_port = cs_tcp_accept_connect.client_port
        #
        log('** /server/accept_connect/accept_sid:%s'%accept_sid)
        self.accept_sid = accept_sid
        self._stop_any_server()
    def engine_on_tcp_accept_condrop(self, cs_tcp_accept_condrop):
        engine = cs_tcp_accept_condrop.engine
        server_sid = cs_tcp_accept_condrop.server_sid
        accept_sid = cs_tcp_accept_condrop.accept_sid
        #
        log('** /server/accept_condrop/accept_sid:%s'%accept_sid)
        self.accept_sid = None
        self._start_server()
    def engine_on_tcp_accept_recv(self, cs_tcp_accept_recv):
        engine = cs_tcp_accept_recv.engine
        accept_sid = cs_tcp_accept_recv.accept_sid
        bb = cs_tcp_accept_recv.bb
        #
        msg = bb.decode('utf8')
        log('** /server/accept_recv/accept_sid:%s/msg:%s'%(accept_sid, msg))
        #
        # send something so that we have data to play with
        bb = bytes(
            source='{echo from server %s} [%s]\n'%(self.spin_h, msg),
            encoding='utf8')
        engine.send(
            sid=accept_sid,
            bb=bb)
    def engine_on_tcp_server_start(self, cs_tcp_server_start):
        engine = cs_tcp_server_start.engine
        server_sid = cs_tcp_server_start.server_sid
        addr = cs_tcp_server_start.addr
        port = cs_tcp_server_start.port
        #
        log('** /server/started/server_sid:%s'%server_sid)
        self.server_sid = server_sid
    def engine_on_tcp_server_stop(self, cs_tcp_server_stop):
        engine = cs_tcp_server_stop.engine
        server_sid = cs_tcp_server_stop.server_sid
        message = cs_tcp_server_stop.message
        #
        log('** /server/stopped/server_sid:%s'%server_sid)
        self.server_sid = None

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
            echo_server = self.engine.init_spin(
                construct=SimpleEchoServer)
            self.servers[spin_h] = echo_server
            echo_server.start(
                ip=ip,
                port=port)
        def on_stop_echo_server(self, spin_h):
            self.servers[spin_h].stop()
            del self.servers[spin_h]
    class CogEvents:
        def __init__(self, cog_h, orb, engine):
            self.cog_h = cog_h
            self.orb = orb
            self.engine = engine
            self.turn_counter = 0
            #
            self.schedule = {
                3: ('x', '127.0.0.1', 4120),
                5: ('y', '127.0.0.1', 4121),
                8: ('z', '127.0.0.1', 4122)}
        def at_turn(self, activity):
            self.turn_counter += 1
            if self.turn_counter in self.schedule:
                (spin_h, ip, port) = self.schedule[self.turn_counter]
                activity.mark(
                    l=self,
                    s='starting server %s'%spin_h)
                self.orb.nearcast(
                    cog=self,
                    message_h='start_echo_server',
                    spin_h=spin_h,
                    ip=ip,
                    port=port)
        def at_close(self):
            pass
    #
    orb = engine.init_orb(
        spin_h='app',
        i_nearcast=i_nearcast)
    orb.add_log_snoop()
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
            echo_server = self.engine.init_spin(
                construct=SimpleEchoServer)
            self.servers[spin_h] = echo_server
            echo_server.start(
                ip=ip,
                port=port)
        def on_stop_echo_server(self, spin_h):
            self.servers[spin_h].stop()
            del self.servers[spin_h]
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
        def at_close(self):
            pass
    #
    orb = engine.init_orb(
        spin_h=__name__,
        i_nearcast=i_nearcast)
    orb.init_cog(CogEvents)
    orb.init_cog(CogServerContainer)
    try:
        engine.event_loop()
    except SolentQuitException:
        pass

def scenario_localhost_tcp_client_and_server(engine):
    print('''
        Testing: look for messages passed between accept and client at bottom.
    ''')
    i_nearcast = '''
        i message h
        i field h

        message start_echo_server
            field ip
            field port

        message stop_echo_server
            field spin_h

        message start_client
            field ip
            field port
        message stop_client
    '''
    class CogClient:
        def __init__(self, cog_h, orb, engine):
            self.cog_h = cog_h
            self.orb = orb
            self.engine = engine
            #
            self.client_sid = None
        def at_close(self):
            if self.client_sid:
                self.engine.close_client(
                    client_sid=self.client_sid)
        def on_start_client(self, ip, port):
            self.engine.open_tcp_client(
                addr=ip,
                port=port,
                cb_tcp_client_connect=self._engine_on_tcp_client_connect,
                cb_tcp_client_condrop=self._engine_on_tcp_client_condrop,
                cb_tcp_client_recv=self._engine_on_tcp_client_recv)
        def on_stop_client(self):
            self.engine.close_tcp_client(
                client_sid=self.client_sid)
        def _engine_on_tcp_client_connect(self, cs_tcp_client_connect):
            engine = cs_tcp_client_connect.engine
            client_sid = cs_tcp_client_connect.client_sid
            addr = cs_tcp_client_connect.addr
            port = cs_tcp_client_connect.port
            #
            #message_to_send_on_connect = 'GET /index.html\n'
            message_to_send_on_connect = 'abcabcabc_from_client\n'
            #
            bb = bytes(message_to_send_on_connect, 'utf8')
            log('** client/client_connect/client_sid:%s/%s/%s'%(client_sid, addr, port))
            self.client_sid = client_sid
            self.engine.send(
                sid=self.client_sid,
                bb=bb)
        def _engine_on_tcp_client_condrop(self, cs_tcp_client_condrop):
            engine = cs_tcp_client_condrop.engine
            client_sid = cs_tcp_client_condrop.client_sid
            message = cs_tcp_client_condrop.message
            #
            log('** client/client_conndrop/client_sid:%s'%(client_sid))
            self.client_sid = None
        def _engine_on_tcp_client_recv(self, cs_tcp_client_recv):
            engine = cs_tcp_client_recv.engine
            client_sid = cs_tcp_client_recv.client_sid
            bb = cs_tcp_client_recv.bb
            #
            msg = bb.decode('utf8')
            log('** client/client_recv/client_sid:%s/msg:%s'%(client_sid, msg))
    class CogEchoServer:
        def __init__(self, cog_h, orb, engine):
            self.cog_h = cog_h
            self.orb = orb
            self.engine = engine
            #
            self.ip = None
            self.port = None
            self.server_sid = None
            self.accept_sid = None
            self.spin_echo_server = engine.init_spin(
                construct=SimpleEchoServer)
        def at_close(self):
            log('** server/at_close')
            if self.server_sid:
                log('*** (stop server)')
                self._stop_server()
            if self.accept_sid:
                log('*** (stop accept)')
                self._boot_accept()
            log('.')
        def on_start_echo_server(self, ip, port):
            self.ip = ip
            self.port = port
            self._start_server()
        def _start_server(self):
            self.engine.open_tcp_server(
                addr=self.ip,
                port=self.port,
                cb_tcp_server_start=self._engine_on_tcp_server_start,
                cb_tcp_server_stop=self._engine_on_tcp_server_stop,
                cb_tcp_accept_connect=self._engine_on_tcp_accept_connect,
                cb_tcp_accept_condrop=self._engine_on_tcp_accept_condrop,
                cb_tcp_accept_recv=self._engine_on_tcp_accept_recv)
        def _stop_server(self):
            self.engine.close_tcp_server(
                server_sid=self.server_sid)
        def _boot_accept(self):
            self.engine.close_accept(
                accept_sid=self.accept_sid)
        def _engine_on_tcp_server_start(self, cs_tcp_server_start):
            engine = cs_tcp_server_start.engine
            server_sid = cs_tcp_server_start.server_sid
            addr = cs_tcp_server_start.addr
            port = cs_tcp_server_start.port
            #
            self.server_sid = server_sid
            log('** server/server_start/server_sid:%s'%(server_sid))
        def _engine_on_tcp_server_stop(self, cs_tcp_server_stop):
            engine = cs_tcp_server_stop.engine
            server_sid = cs_tcp_server_stop.server_sid
            message = cs_tcp_server_stop.message
            #
            self.server_sid = None
            log('** server/server_stop/server_sid:%s'%(server_sid))
        def _engine_on_tcp_accept_connect(self, cs_tcp_accept_connect):
            engine = cs_tcp_accept_connect.engine
            server_sid = cs_tcp_accept_connect.server_sid
            accept_sid = cs_tcp_accept_connect.accept_sid
            client_addr = cs_tcp_accept_connect.client_addr
            client_port = cs_tcp_accept_connect.client_port
            #
            log('** server/accept_connect/accept_sid:%s'%(accept_sid))
            self._stop_server()
            self.accept_sid = accept_sid
            #
            # send some text so we have something to woork with
            message_to_send_on_connect = 'abcabcabc_from_accept\n'
            #
            bb = bytes(message_to_send_on_connect, 'utf8')
            log('** client/accept_connect/accept_sid:%s/%s/%s'%(accept_sid, addr, port))
            self.accept_sid = accept_sid
            self.engine.send(
                sid=accept_sid,
                bb=bb)
        def _engine_on_tcp_accept_condrop(self, cs_tcp_accept_condrop):
            engine = cs_tcp_accept_condrop.engine
            server_sid = cs_tcp_accept_condrop.server_sid
            accept_sid = cs_tcp_accept_condrop.accept_sid
            #
            log('** server/accept_condrop/accept_sid:%s'%(accept_sid))
            self.accept_sid = None
            self._start_server()
        def _engine_on_tcp_accept_recv(self, cs_tcp_accept_recv):
            engine = cs_tcp_accept_recv.engine
            accept_sid = cs_tcp_accept_recv.accept_sid
            bb = cs_tcp_accept_recv.bb
            #
            msg = bb.decode('utf8')
            log('** server/accept_recv/accept_sid:%s/msg:%s'%(accept_sid, msg))
    class CogBridge:
        def __init__(self, cog_h, orb, engine):
            self.cog_h = cog_h
            self.orb = orb
            self.engine = engine
        def nc_start_client(self, ip, port):
            self.nearcast.start_client(
                ip=ip,
                port=port)
        def nc_start_echo_server(self, ip, port):
            self.nearcast.start_echo_server(
                ip=ip,
                port=port)
    #
    orb = engine.init_orb(
        spin_h='app',
        i_nearcast=i_nearcast)
    orb.init_cog(CogClient)
    orb.init_cog(CogEchoServer)
    bridge = orb.init_cog(CogBridge)
    #
    addr = 'localhost'
    port = 5000
    bridge.nc_start_echo_server(
        ip=addr,
        port=port)
    bridge.nc_start_client(
        ip=addr,
        port=port)
    #
    engine.event_loop()

def scenario_tcp_client_edge_cases(engine):
    print('''
        Testing: this scenario is currently more laborious than the others. If
        you want to exercise this function, then you need to enable the
        addr/port pairs in the code one by one and see what they do.
    ''')
    i_nearcast = '''
        i message h
        i field h

        message start_client
            field ip
            field port
        message stop_client
    '''
    class CogClient:
        def __init__(self, cog_h, orb, engine):
            self.cog_h = cog_h
            self.orb = orb
            self.engine = engine
            #
            self.client_sid = None
        def at_close(self):
            if self.client_sid:
                self.engine.close_client(
                    client_sid=self.client_sid)
        def on_start_client(self, ip, port):
            self.engine.open_tcp_client(
                addr=ip,
                port=port,
                cb_tcp_client_connect=self._engine_on_tcp_client_connect,
                cb_tcp_client_condrop=self._engine_on_tcp_client_condrop,
                cb_tcp_client_recv=self._engine_on_tcp_client_recv)
        def on_stop_client(self):
            self.engine.close_tcp_client(
                client_sid=self.client_sid)
        def _engine_on_tcp_client_connect(self, cs_tcp_client_connect):
            engine = cs_tcp_client_connect.engine
            client_sid = cs_tcp_client_connect.client_sid
            addr = cs_tcp_client_connect.addr
            port = cs_tcp_client_connect.port
            #
            #message_to_send_on_connect = 'GET /index.html\n'
            message_to_send_on_connect = 'abcabcabc_from_client\n'
            #
            log('** connect/%s/%s/%s'%(client_sid, addr, port))
            #
            # send a bb so we can see some activity
            bb = bytes(message_to_send_on_connect, 'utf8')
            self.client_sid = client_sid
            self.engine.send(
                sid=self.client_sid,
                bb=bb)
        def _engine_on_tcp_client_condrop(self, cs_tcp_client_condrop):
            engine = cs_tcp_client_condrop.engine
            client_sid = cs_tcp_client_condrop.client_sid
            message = cs_tcp_client_condrop.message
            #
            log('** conndrop callback %s'%(client_sid))
            self.client_sid = None
        def _engine_on_tcp_client_recv(self, cs_tcp_client_recv):
            engine = cs_tcp_client_recv.engine
            client_sid = cs_tcp_client_recv.client_sid
            bb = cs_tcp_client_recv.bb
            #
            log('** client recv [%s]'%(bb.decode('utf8')))
    class CogBridge:
        def __init__(self, cog_h, orb, engine):
            self.cog_h = cog_h
            self.orb = orb
            self.engine = engine
        def nc_start_client(self, ip, port):
            self.nearcast.start_client(
                ip=ip,
                port=port)
    #
    orb = engine.init_orb(
        spin_h='app',
        i_nearcast=i_nearcast)
    orb.init_cog(CogClient)
    bridge = orb.init_cog(CogBridge)
    #
    # Exercise: bad ip
    # Setup: none
    # Expect: ??
    #addr = '203.15.93.2'
    #port = 5000
    #
    # Exercise: bad domain name
    # Setup: none
    # Expect: At the moment it exits with an exception. There's future work to
    # be done to wrap the connect_ex with a try/except, and when that happens
    # to elegantly close the metasock. This is not particularly important, and
    # there is a fair chance of nasty edge cases coming through, so for the
    # moment we don't worry about it. When we come to it, this test is ready.
    #addr = 'xxx_bad_addr'
    #port = 80
    #
    # Exercise: netcat to localhost, with localhost not listening
    # Setup: none
    # Expect: ECONNREFUSED
    #addr = '127.0.0.1'
    #port = 5000
    #
    # Exercise: localhost netcat, working
    # Setup: nc -l -p 5000
    # Expect: Successful connection
    #addr = '127.0.0.1'
    #port = 5000
    #
    # Exercise: songseed netcat
    # Setup: ncat -l -p 5000
    # Expect: this client end will send a message to the netcat accept end
    #addr = 'songseed.org'
    #port = 5000
    #
    # Exercise: songseed webserver
    # Setup: none, so long as songseed webserver is running
    # Expect: a HTML error page. (or change the send message in code above)
    addr = 'songseed.org'
    port = 80
    bridge.nc_start_client(
        ip=addr,
        port=port)
    #
    engine.event_loop()

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
        (This is becomming redundant with the extra-strong client
        tests in previous scenario. However, keep for the moment
        until we know how to better break those out.)
    ''')
    #
    class Spin:
        def __init__(self, spin_h, engine):
            self.spin_h = spin_h
            self.engine = engine
        def at_turn(self, activity):
            while self.received:
                log('client|%s'%(self.received.popleft().strip()))
        def at_close(self):
            pass
        #
        def start(self, name, addr, port):
            self.name = name
            self.addr = addr
            self.port = port
            # form: (addr, port) : deque containing data
            self.received = None
            self.sid = engine.open_tcp_client(
                addr=addr,
                port=port,
                cb_tcp_client_connect=self.engine_on_tcp_client_connect,
                cb_tcp_client_condrop=self.engine_on_tcp_client_condrop,
                cb_tcp_client_recv=self.engine_on_tcp_client_recv)
        def engine_on_tcp_client_connect(self, cs_tcp_client_connect):
            engine = cs_tcp_client_connect.engine
            client_sid = cs_tcp_client_connect.client_sid
            addr = cs_tcp_client_connect.addr
            port = cs_tcp_client_connect.port
            #
            log('connect/%s/%s/%s'%(client_sid, addr, port))
            self.received = deque()
        def engine_on_tcp_client_condrop(self, cs_tcp_client_condrop):
            engine = cs_tcp_client_condrop.engine
            client_sid = cs_tcp_client_condrop.client_sid
            message = cs_tcp_client_condrop.message
            #
            self.received = None
            log('** conndrop callback %s'%(client_sid))
        def engine_on_tcp_client_recv(self, cs_tcp_client_recv):
            engine = cs_tcp_client_recv.engine
            client_sid = cs_tcp_client_recv.client_sid
            bb = cs_tcp_client_recv.bb
            #
            self.received.append(bb)
    #
    details = { 'p': ('localhost', 1233)
              }
    for (name, (addr, port)) in details.items():
        spin = engine.init_spin(
            construct=Spin)
        spin.start(name, addr, port)
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
    class Spin:
        def __init__(self, spin_h, engine):
            self.spin_h = spin_h
            self.engine = engine
        def at_turn(self, activity):
            if self.b_dropped:
                return
            while self.received:
                activity.mark(
                    l='scenario_tcp_client_mixed_scenarios',
                    s='received data from net')
                log('client|%s'%(self.received.popleft().strip()))
            if self.turn_count == self.close_turn:
                log('closing %s/%s on turn %s'%(
                    self.name, self.sid, self.orb.turn_count))
                activity.mark(
                    l='scenario_tcp_client_mixed_scenarios',
                    s='reached turn count')
                self.engine.close_tcp_client(self.sid)
                self.engine.del_spin(
                    spin_h=self.spin_h)
                self.sid = None
            self.turn_count += 1
        def at_close(self):
            pass
        #
        def start(self, name, orb, addr, port, close_turn):
            self.name = name
            self.orb = orb
            self.addr = addr
            self.port = port
            self.close_turn = close_turn
            #
            self.turn_count = 0
            self.sid = engine.open_tcp_client(
                addr=addr,
                port=port,
                cb_tcp_client_connect=self.engine_on_tcp_client_connect,
                cb_tcp_client_condrop=self.engine_on_tcp_client_condrop,
                cb_tcp_client_recv=self.engine_on_tcp_client_recv)
            self.b_dropped = False
            # form: (addr, port) : deque containing data
            self.received = None
        def engine_on_tcp_client_connect(self, cs_tcp_client_connect):
            engine = cs_tcp_client_connect.engine
            client_sid = cs_tcp_client_connect.client_sid
            addr = cs_tcp_client_connect.addr
            port = cs_tcp_client_connect.port
            #
            log('connect/%s/%s/%s'%(client_sid, addr, port))
            self.received = deque()
            self.b_dropped = False
        def engine_on_tcp_client_condrop(self, cs_tcp_client_condrop):
            engine = cs_tcp_client_condrop.engine
            client_sid = cs_tcp_client_condrop.client_sid
            message = cs_tcp_client_condrop.message
            #
            log("condrop/%s/%s/%s"%(self.name, client_sid, message))
            self.received = None
            self.b_dropped = True
        def engine_on_tcp_client_recv(self, cs_tcp_client_recv):
            engine = cs_tcp_client_recv.engine
            client_sid = cs_tcp_client_recv.client_sid
            bb = cs_tcp_client_recv.bb
            #
            self.received.append(bb)
    #
    # ports we will create
    details = { 'p': ('songseed.org', 22, 7)
              , 'q': ('localhost', 1234, 12)
              }
    for (name, (addr, port, close_turn)) in details.items():
        spin = engine.init_spin(
            construct=Spin)
        spin.start(
            name=name,
            orb=spin,
            addr=addr,
            port=port,
            close_turn=close_turn)
    #
    # here we go!
    engine.event_loop()

class SpinPublisher:
    def __init__(self, spin_h, engine):
        self.spin_h = spin_h
        self.engine = engine
        #
        self.last_t = 0
        self.count_turns = 0
        self.b_launched = False
        self.addr = None
        self.port = None
        self.pub_sid = None
    def at_turn(self, activity):
        if not self.b_launched:
            return
        #
        # On a turn interval, we raise and lower the publisher
        self.count_turns += 1
        if self.count_turns == 5:
            self.count_turns = 0
            activity.mark(
                l=self,
                s='count interval')
            if self.pub_sid == None:
                self._start_server()
            else:
                self._stop_server()
        #
        # Periodically, we send something the network
        if None != self.pub_sid:
            t = time.time()
            if t - self.last_t > 4:
                log('** sending')
                activity.mark(
                    l=self,
                    s='two seconds passed')
                self.last_t = t
                bb = bytes(
                    source='from poke [%s]'%t,
                    encoding='utf8')
                self.engine.send(
                    sid=self.pub_sid,
                    bb=bb)
    def at_close(self):
        self.b_launched = False
        if self.pub_sid != None:
            self._stop_server()
    def go(self, addr, port):
        self.addr = addr
        self.port = port
        #
        self.b_launched = True
        self._start_server()
    def _engine_on_pub_start(self, cs_pub_start):
        engine = cs_pub_start.engine
        pub_sid = cs_pub_start.pub_sid
        addr = cs_pub_start.addr
        port = cs_pub_start.port
        #
        self.pub_sid = pub_sid
        log('pub start %s'%(self.pub_sid))
    def _engine_on_pub_stop(self, cs_pub_stop):
        engine = cs_pub_stop.engine
        pub_sid = cs_pub_stop.pub_sid
        message = cs_pub_stop.message
        #
        log('pub stop %s'%(self.pub_sid))
        self.pub_sid = None
    def _start_server(self):
        if None != self.pub_sid:
            raise Exception("Already running.")
        self.engine.open_pub(
            addr=self.addr,
            port=self.port,
            cb_pub_start=self._engine_on_pub_start,
            cb_pub_stop=self._engine_on_pub_stop)
    def _stop_server(self):
        if None == self.pub_sid:
            raise Exception("No server currently started.")
        self.engine.close_pub(
            pub_sid=self.pub_sid)

def scenario_pub(engine):
    #
    # This is not a good style example. Predates nearcasting.
    #
    addr = '127.255.255.255'
    port = 50000
    log('''You can watch this data with the qd_listen tool:
        python3 -m solent.tools.qd_listen %s %s'''%(addr, port))
    #
    #
    spin_publisher = engine.init_spin(
        construct=SpinPublisher)
    spin_publisher.go(
        addr=addr,
        port=port)
    #
    #engine.debug_eloop_on()
    engine.event_loop()

def main():
    init_logging()

    engine = engine_new(
        mtu=1492)
    try:
        #
        # Comment these in or out as you want to test scenarios.
        #
        scenario_basic_nearcast_example(engine)
        #scenario_sub_simple(engine)
        #scenario_sub_listen_and_unlisten(engine)
        #scenario_multiple_tcp_servers(engine)
        #scenario_close_tcp_servers(engine)
        #scenario_localhost_tcp_client_and_server(engine)
        #scenario_tcp_client_edge_cases(engine)
        #scenario_tcp_client_cannot_connect(engine)
        #scenario_tcp_client_mixed_scenarios(engine)
        #scenario_pub(engine)
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

