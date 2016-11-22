#
# cog_gruel_client
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

from solent.eng import log

from collections import deque
from collections import OrderedDict as od


# --------------------------------------------------------
#   :layers
# --------------------------------------------------------
#
# Layers are a concept that are currently defined just for the purpose of this
# module. Each layer represents a layer of responsibility involved in the
# control of the network protocol.
#
# This pattern seeks to be an elegant alternative to the kind of if-block
# spaghetti that is typical of network programming.
#
# Imagine that there is a row of layers. The layer that is first in line has
# certain responsibilities. If they're not met, then the process doesn't
# continue. If they are met, then the layer passes the conch to the next
# layer. This process happens once per turn.
#

class ConnectionIntentLayer:
    '''
    Key responsibility: do we want to be connected to the server or not?
    '''
    def __init__(self, cog_gruel_client):
        self.cog_gruel_client = cog_gruel_client
        #
        self.state = ns()
        self._zero()
    #
    def _zero(self):
        self.state.is_open = False
    def _to_open(self):
        # To be called when we transition to open.
        self.state.is_open = True
    def _to_shut(self):
        # To be called when we transition to shut.
        self._zero()
    #
    def is_open(self):
        return self.state.is_open
    def be_open(self):
        if not self.is_open():
            self._to_open()
    def be_shut(self):
        if self.is_open():
            self._to_shut()
    #
    def at_turn(self, activity):
        # This is only called when the layer is open.
        pass

class TcpConnectionLayer:
    '''
    Key responsibility: are we connected to the server or not?
    '''
    def __init__(self, cog_gruel_client):
        self.cog_gruel_client = cog_gruel_client
        #
        self.state = ns()
        self._zero()
    #
    def _zero(self):
        self.state.is_open = False
    def _to_open(self):
        # To be called when we transition to open.
        self.state.is_open = True
    def _to_shut(self):
        # To be called when we transition to shut.
        self._zero()
    #
    def is_open(self):
        return self.state.is_open
    def be_open(self):
        if not self.is_open():
            self._to_open()
    def be_shut(self):
        if self.is_open():
            self._to_shut()
    #
    def at_turn(self, activity):
        # This is only called when the layer is open.
        pass

class LogonLayer:
    '''
    Key responsibility: are we logged on or not?
    '''
    def __init__(self, cog_gruel_client):
        self.cog_gruel_client = cog_gruel_client
        #
        self.state = ns()
        self._zero()
    #
    def _zero(self):
        self.state.is_open = False
    def _to_open(self):
        # To be called when we transition to open.
        self.state.is_open = True
    def _to_shut(self):
        # To be called when we transition to shut.
        self._zero()
    #
    def is_open(self):
        return self.state.is_open
    def be_open(self):
        if not self.is_open():
            self._to_open()
    def be_shut(self):
        if self.is_open():
            self._to_shut()
    #
    def at_turn(self, activity):
        # This is only called when the layer is open.
        pass

class HeartbeatLayer:
    '''
    Key responsibility: periodically respond to server heartbeats.
    '''
    def __init__(self, cog_gruel_client):
        self.cog_gruel_client = cog_gruel_client
        #
        self.state = ns()
        self._zero()
    #
    def _zero(self):
        self.state.is_open = False
    def _to_open(self):
        # To be called when we transition to open.
        self.state.is_open = True
    def _to_shut(self):
        # To be called when we transition to shut.
        self._zero()
    #
    def is_open(self):
        return self.state.is_open
    def be_open(self):
        if not self.is_open():
            self._to_open()
    def be_shut(self):
        if self.is_open():
            self._to_shut()
    #
    def at_turn(self, activity):
        # This is only called when the layer is open.
        pass

class OutgoingsLayer:
    '''
    Key responsibility: is there content to be dispatched to the server?
    '''
    def __init__(self, cog_gruel_client):
        self.cog_gruel_client = cog_gruel_client
        #
        self.state = ns()
        self._zero()
    #
    def _zero(self):
        self.state.is_open = False
    def _to_open(self):
        # To be called when we transition to open.
        self.state.is_open = True
    def _to_shut(self):
        # To be called when we transition to shut.
        self._zero()
    #
    def is_open(self):
        return self.state.is_open
    def be_open(self):
        if not self.is_open():
            self._to_open()
    def be_shut(self):
        if self.is_open():
            self._to_shut()
    #
    def at_turn(self, activity):
        # This is only called when the layer is open.
        pass

class PackagingLayer:
    '''
    Key responsibility: is there a packet to be dispatched to the server?
    '''
    def __init__(self, cog_gruel_client):
        self.cog_gruel_client = cog_gruel_client
        #
        self.state = ns()
        self._zero()
    #
    def _zero(self):
        self.state.is_open = False
    def _to_open(self):
        # To be called when we transition to open.
        self.state.is_open = True
    def _to_shut(self):
        # To be called when we transition to shut.
        self._zero()
    #
    def is_open(self):
        return self.state.is_open
    def be_open(self):
        if not self.is_open():
            self._to_open()
    def be_shut(self):
        if self.is_open():
            self._to_shut()
    #
    def at_turn(self, activity):
        # This is only called when the layer is open.
        pass


# --------------------------------------------------------
#   :rest
# --------------------------------------------------------
#
# xxx
'''
engine.open_tcp_client(
    addr=addr,
    port=port,
    cb_tcp_connect=self.engine_on_tcp_connect,
    cb_tcp_confail=self.engine_on_tcp_confail,
    cb_tcp_recv=self.engine_on_tcp_recv)
'''

class CogGruelClient:
    def __init__(self, cog_h, nearcast_orb, engine, addr, port):
        self.cog_h = cog_h
        self.nearcast_orb = nearcast_orb
        self.engine = engine
        self.addr = addr
        self.port = port
        #
        self.connection_intent_layer = ConnectionIntentLayer(self)
        self.tcp_connection_layer = TcpConnectionLayer(self)
        self.logon_layer = LogonLayer(self)
        self.heartbeat_layer = HeartbeatLayer(self)
        self.outgoings_layer = OutgoingsLayer(self)
        self.packaging_layer = PackagingLayer(self)
        #
        # form: (addr, port) : deque containing data
        self.q_received = deque()
        self.client_sid = None
    def close(self):
        self.engine.close_tcp_server(self.server_sid)
    def at_turn(self):
        "Returns a boolean which is True only if there was activity."
        activity = False
        return activity
    #
    def on_send_something(self, text):
        pass
    #
    def engine_on_tcp_connect(self, cs_tcp_connect):
        engine = cs_tcp_connect.engine
        client_sid = cs_tcp_connect.client_sid
        addr = cs_tcp_connect.addr
        port = cs_tcp_connect.port
        #
        log("connect/%s/%s/%s/%s"%(
            self.cog_h,
            client_sid,
            addr,
            port))
        engine.send(
            sid=client_sid,
            data='')
    def engine_on_tcp_confail(self, cs_tcp_confail):
        engine = cs_tcp_confail.engine
        client_sid = cs_tcp_confail.client_sid
        message = cs_tcp_confail.message
        #
        log("confail/%s/%s/%s"%(self.cog_h, client_sid, message))
        while self.q_received:
            self.q_received.pop()
    def engine_on_tcp_recv(self, cs_tcp_recv):
        engine = cs_tcp_recv.engine
        client_sid = cs_tcp_recv.client_sid
        data = cs_tcp_recv.data
        #
        self.q_received.append(data)
        engine.send(
            sid=client_sid,
            data='q_received %s\n'%len(data))

def cog_gruel_client_new(cog_h, nearcast_orb, engine, addr, port):
    ob = CogGruelClient(
        cog_h=cog_h,
        nearcast_orb=nearcast_orb,
        engine=engine,
        addr=addr,
        port=port)
    return ob

