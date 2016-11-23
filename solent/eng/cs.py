#
# Callback structures
# 
# Each of these structs represents a kind of message that can be passed from
# the engine to user code via a callback.
#
# //
# // notes for users of the engine
#
# Use-case: you are here because you want to understand the circumstances
# for which you will get one of these callback structs.
#
# Action: read the pydocs associated with each of the classes below.
#
# Callback structures are used when engine/metasock calls back to an
# application that is using the engine. If you need an explanation
# for what the different kinds of callback are, look at the 
#
# //
# // implementation notes
#
# Use-case: you want to understand why you get these struct things rather
# than parameters.
#
# Indeed. The design/behavior of these callback structs is unusual for python.
#
# Why? This system has been designed with an intention that we should be able
# to directly port the whole thing to C later on. In particular, eng could
# be converted to C and given a python wrapper. This interest takes priority
# over pythonic coding style, and this is one of the areas where this is
# obvious.
#
# You might say, "why did you not instead pass multiple arguments to the
# callback methods." Indeed, that was the behaviour in an earlier version of
# this code. This design sets things up for a C port more easily.
#
# Each of these structs has a prefix, Cs. This implies callback struct.
#
# //
# // more implementation notes
#
# Use-case: you've been reading the engine/metasock code, and note that these
# are created as singletons. You think this is odd and want to know more.
#
# As above, we may port this codebase to C later. This priority leads us
# towards practices that avoid heap allocations (i.e. practices that create
# new objects).
#
# Within the engine, we want to avoid allocating memory every time we do a
# callback. So. Instead of that, Metasock creates a single instance of each of
# these structs. We reuse that struct whenever we make a callback.
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

class CsTcpConnect(object):
    '''Data that is sent in the callback announcing that an attempt to
    establish a TCP connection has been successful.
    '''
    def __init__(self):
        self.engine = None
        self.client_sid = None
        self.addr = None
        self.port = None
    def __repr__(self):
        return '(%s%s)'%(self.__class__.__name__, '|'.join([str(x) for x in
            [self.engine, self.client_sid, self.addr, self.port]]))

class CsTcpCondrop(object):
    '''Data that is sent in the callback announcing any kind of dropped TCP
    connection /or connection attempt/.
    Let's just cover those scenarios.
        * You are making an outbound tcp client connection, and it doesn't get
          established.
        * You have made a successful outbound trp client connection, and then
          it mysteriously drops.
        * You have made a successful outbound trp client connection, and then
          you close it deliberately.
        * You are running a TCP server, and a third party has a TCP connection
          to you via that server. Now, they disconnect.
    #
    Emphasis: this system tries to give non-server connections a consistent
    behaviour regardless of who initiated the connection. Hence, outbound
    and server-hosted client sockets are massaged into a common behaviour.
    '''
    def __init__(self):
        self.engine = None
        # Maintainers: please do not refactor this to sid. It's important that
        # the receiver of this callback struct clearly understands that the sid
        # they get back from this callback is distinct from any server sids that
        # may also be running.
        self.client_sid = None
        self.message = None
    def __repr__(self):
        return '(%s%s)'%(self.__class__.__name__, '|'.join([str(x) for x in
            [self.engine, self.client_sid, self.message]]))

class CsTcpRecv(object):
    '''This callback struct relates to the behaviour of client connections.
    When a client connection gets data, a callback will trigger that
    contains an instance of this.
    '''
    def __init__(self):
        self.engine = None
        self.client_sid = None
        self.data = None
    def __repr__(self):
        return '(%s%s)'%(self.__class__.__name__, '|'.join([str(x) for x in
            [self.engine, self.client_sid, self.data]]))

class CsSubRecv(object):
    '''Similar to CsTcpRecv, but designed for subscribers. It's useful
    to distinguish, because this discourages a naive user in a large codebase
    from trying to send traffic over a sub sid.
    '''
    def __init__(self):
        self.engine = None
        self.sub_sid = None
        self.data = None
    def __repr__(self):
        return '(%s%s)'%(self.__class__.__name__, '|'.join([str(x) for x in
            [self.engine, self.sub_sid, self.data]]))

class CsMsClose(object):
    '''You don't need to be aware of this structure you're coming to grips
    with engine/metasock.
    
    This callback struct is used for coordinating close events between engine
    and metasock. User code should never be concerned with it. In particular,
    it has to do with the shutdown of sockets during an event loop. Don't
    confuse this with CsTcpCondrop.
    '''
    def __init__(self):
        self.ms = None
        self.sid = None
        self.message = None
    def __repr__(self):
        return '(%s%s)'%(self.__class__.__name__, '|'.join([str(x) for x in
            [self.ms, self.sid, self.message]]))

