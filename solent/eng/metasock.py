#
# metasock
#
# // overview
# Unless you are working on the engine, you should never need to look at
# this class. (And nor would you want to.)
#
# Should you decide to press on, first read the pydoc for the Metasock class
# below.
#
# In here and in engine, you'll find laboriously detailed notes about
# implementation. Usually this is something to avoid. Comments that annotate
# implementation make code brittle. Comments that describe the implementation
# of other parts of the codebase are much worse. But this settlement is not an
# accident.
#
#   a verbose defense of all the verbose commenting
#   ========================================================
#   In the case of this system (engine+metasock), I've found it necessary to
#   write small essays all through the code. The Berkeley sockets API is
#   complicated, and it's only through heavy annotation that I have been able
#   to get this code to a point where I can reason about it when I try to
#   recall why the hell I did something a particular way.
#
#   As a general rule, heavy documentation is an obstacle to someone who
#   wanted to change code, and creates maintenance risk. But in this case,
#   heavy documentation is justified.
#
#   This class + engine are attempting a difficult task: producing a clean
#   facade around the Berkeley sockets API. The nastiness has caused me to
#   intertwine these two classes in a manner that goes far beyond what is
#   desirable in typical OO code. The comments seek to highlight the
#   intertwined section, and to explain weird sections by highlighting the
#   Berkeley API pitfalls that overcome.
#
#   Generally, code should be written to be maintained. But these two classes
#   are mature and intertwined enough that I don't expect there will be much
#   further structural maintenance on them. But I do find myself reading
#   through sections regularly, and the comments are what allow me to
#   understand what's going on.
#   ========================================================
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

from .cs import CsMsClose, CsTcpConnect, CsTcpCondrop, CsTcpRecv, CsSubRecv

from solent.log import hexdump_bytes
from solent.log import log

from collections import deque
import socket
import traceback

def l_cb_error(cb_struct):
    def fn(*args):
        raise Exception(cb_struct)
    return fn

class MetasockCloseCondition(Exception):
    def __init__(self, message):
        self.message = message

class Metasock(object):
    """This is a mechanism for creating a socket with intent.
    
    // Huh?

    Let's talk about the problem it solves. When you create a socket normally,
    there is no way to indicate whether you would like for it to be read from
    or written to. You have to keep that info separate. An instance of this
    class tracks whether you want for it to be read from or written to, and
    that info can be used for contructing a select call on the fly.

    // A more technical summary

    This is an integral piece to an attempt to build a means to create
    asynchronous event loops that scale easily from the perspective of the
    application programmer.

    // Anything else?

    This uses callbacks for recv. That means that the select loop can work
    like this: (1) find all the metasockets that need reading from and writing
    to; (2) carry around a surgical select on that basis; (3) lookup the
    metasocket that corresponds to the sockets you get back from the select.
    (4) call read / write on them as appropriate. For recv, the metasocket
    can just funnel any content it gets to its callbacks

    Also, you see that there's a callback for when the thing is closed.
    This is necessary because sometimes you learn that it's appropriate
    to do a close while you're trying to do a read and a send. In these
    cases I catch the exception and then pass a callback. And since I'd
    done that, it makes sense to call that whenever I do a close (even
    one that has been explicitly called) because that will allow the caller
    to keep all of the cleanup logic in a single place.
    """
    def __init__(self, engine, mempool, sid, addr, port):
        self.engine = engine
        self.mempool = mempool
        self.sid = sid
        self.addr = addr
        self.port = port
        #
        self.sock = None
        #
        self.can_it_recv = False
        self.recv_len = None
        #
        self.can_it_send = False
        self.send_buf = deque() # buffers sips
        #
        self.is_it_a_tcp_server = False
        self.is_it_a_tcp_client = False
        self.is_tcp_client_connecting = False
        #
        self.cb_tcp_connect = l_cb_error('cb_tcp_connect not set')
        self.cs_tcp_connect = CsTcpConnect()
        self.cb_tcp_condrop = l_cb_error('cb_tcp_condrop not set')
        self.cs_tcp_condrop = CsTcpCondrop()
        self.cb_sub_recv = l_cb_error('cb_sub_recv not set')
        self.cs_sub_recv = CsSubRecv()
        self.cb_tcp_recv = l_cb_error('cb_tcp_recv not set')
        self.cs_tcp_recv = CsTcpRecv()
        #
        # This is designed to be a callback into the engine, to help the
        # engine track sockets that close during an event loop. Don't confuse
        # it with condrop.
        self.cb_ms_close = l_cb_error('cb_ms_close not set')
        self.cs_ms_close = CsMsClose()
    def desires_recv(self):
        return self.can_it_recv
    def desires_send(self):
        if not self.can_it_send:
            return False
        if not self.send_buf:
            return False
        return True
    def close(self, message):
        '''Safely attempts to close the socket, and then triggers the
        callback to say that it has done (cb_ms_close). This should be
        called from one place and one place only - engine._close_metasock.
        '''
        # If you find yourself tempted to do /anything/ here other than
        # closing the socket and triggering the callback to say that you have
        # done, there's a problem with your abstractions, and you need to deal
        # with that right away. To make the same point another way - do not
        # put anything else in here, or else you'll break the behaviour of a
        # bunch of edge-cases.
        #
        # Something to think about on that topic. If we find ourselves in a
        # situation where we really feel forced towards that, we may have run
        # out of room to handle this using a non-OO approach. In that case,
        # a direction to think of is interfacing, with an addition of
        # precloe and postclose functions.
        try:
            self.sock.close()
        except:
            pass
        #
        if self.is_it_a_tcp_client:
            self.cs_tcp_condrop.engine = self.engine
            self.cs_tcp_condrop.client_sid = self.sid
            self.cs_tcp_condrop.message = message
            self.cb_tcp_condrop(
                cs_tcp_condrop=self.cs_tcp_condrop)
        #
        self.cs_ms_close.ms = self
        self.cs_ms_close.message = message
        self.cb_ms_close(
            cs_ms_close=self.cs_ms_close)
    def copy_to_send_queue(self, sip):
        self.send_buf.append(
            self.mempool.clone(sip))
    def manage_send(self):
        if not self.can_it_send:
            raise Exception("%s is not a send sock."%self.sid)
        try:
            while self.send_buf:
                sip = self.send_buf.popleft()
                bb = sip.get()
                send_size = self.sock.send(bb)
                if send_size == len(bb):
                    # Ideal situation: we sent the payload
                    self.mempool.free(
                        sip=sip)
                    continue
                elif 0 == send_size:
                    # Network conjestion or slow throughput by the reader
                    # is causing things to back up. This will happen from
                    # time to time in normal operation.
                    self.send_buf.appendleft(sip)
                    break
                else:
                    # This is weird. Since our payload must be smaller than
                    # the MTU size, this should never happen.
                    raise Algorithm("Weird: partial payload send. %s of %s"%(
                        send_size, len(bb)))
        except:
            # When you try to do a send to a BSD socket that is in the
            # process of going down, you can get an exception. This caterss
            # for that scenario.
            raise MetasockCloseCondition('send_fail')
            return
    def manage_recv(self, cb_ms_close):
        '''
        Here, we receive a var cb_ms_close. This might seem strange: why send
        in a callback for closing when we are instructing a receive?

        Short explanation: in the Berkeley sockets API, there is a race
        condition that is inherent to the way that recv works. We need to have
        a close callback on-hand in case it fires.

        Longer explanation: consider this scenario. A call to select(..)
        elsewhere has told us that we can do a recv. But while we are getting
        organised to do that, the sock closes. We will know from the recv that
        the socket has died, and we need to handle that situation. This
        cb_ms_close is what allows us to do that. (bsd socket api is awful!)
        '''
        #
        # In Berkeley sockets, an indication that a server socket is
        # ready-to-read means something completely different to an indication
        # that a client socket is ready-to-read. Here we split these
        # behaviours into different codepaths.
        #
        # // server socket codepath
        if self.is_it_a_tcp_server:
            (csock, (addr, port)) = self.sock.accept()
            #
            client_sid = self.engine.register_accepted_tcp_csock(
                csock=csock,
                addr=addr,
                port=port,
                cb_tcp_condrop=self.cb_tcp_condrop,
                cb_tcp_recv=self.cb_tcp_recv,
                cb_ms_close=cb_ms_close)
            #
            self.cs_tcp_connect.engine = self.engine
            self.cs_tcp_connect.client_sid = client_sid
            self.cs_tcp_connect.addr = addr
            self.cs_tcp_connect.port = port
            self.cb_tcp_connect(
                cs_tcp_connect=self.cs_tcp_connect)
            return
        #
        # // non-server socket codepath
        try:
            data = self.sock.recv(self.recv_len)
        except Exception as e:
            # If you're going to disappear errors here, do it with an
            # exception that is specific to a real read_fail. Note,
            # * You can't count on e.message existing
            # * Ugly string comparison might be the only way to do it
            log('recv exception [sid %s] [%s]'%(self.sid, str(e)))
            raise MetasockCloseCondition('read_fail')
            return
        if data in (None,) or 0 == len(data):
            # In this case, it's presumed that select told you that it
            # was good to read from this, and yet when you went to read
            # there wasn't anything empty. This indicates that it's time
            # to close the socket, which we'll now do.
            #
            # Note that we're telling the network engine that we're done
            # here, and not calling our own close method directly. This
            # is so that cleanup happens properly.
            self.engine._close_metasock(self.sid, 'empty_recv')
            return
        #
        if self.is_it_a_tcp_client:
            hexdump_bytes(
                arr=data,
                title='** metasock client read**')
            self.cs_tcp_recv.data = data
            self.cs_tcp_recv.engine = self.engine
            self.cs_tcp_recv.client_sid = self.sid
            self.cb_tcp_recv(
                cs_tcp_recv=self.cs_tcp_recv)
        else:
            # assume it's a udp or multicast subscriber
            self.cs_sub_recv.data = data
            self.cs_sub_recv.engine = self.engine
            self.cs_sub_recv.sub_sid = self.sid
            self.cb_sub_recv(
                cs_sub_recv=self.cs_sub_recv)
    def successful_connection_as_tcp_client(self):
        self.is_tcp_client_connecting = False
        #
        self.cs_tcp_connect.engine = self.engine
        self.cs_tcp_connect.client_sid = self.sid
        self.cs_tcp_connect.addr = self.addr
        self.cs_tcp_connect.port = self.port
        self.cb_tcp_connect(
            cs_tcp_connect=self.cs_tcp_connect)

def metasock_create_broadcast_listener(engine, mempool, sid, addr, port, cb_sub_recv):
    log('metasock_create_broadcast_listener %s (%s:%s)'%(sid, addr, port))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((addr, port))
    sock.setblocking(0)
    #
    ms = Metasock(
        engine=engine,
        mempool=mempool,
        sid=sid,
        addr=addr,
        port=port)
    ms.sock = sock
    ms.can_it_recv = True
    ms.can_it_send = False
    ms.recv_len = engine.mtu
    ms.cb_sub_recv = cb_sub_recv
    return ms

def metasock_create_tcp_server(engine, mempool, sid, addr, port, cb_tcp_connect, cb_tcp_condrop, cb_tcp_recv):
    log('metasock_create_tcp_server %s (%s:%s)'%(sid, addr, port))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((addr, port))
    sock.setblocking(0)
    sock.listen(0)
    #
    ms = Metasock(
        engine=engine,
        mempool=mempool,
        sid=sid,
        addr=addr,
        port=port)
    ms.sock = sock
    ms.can_it_recv = True
    ms.can_it_send = True
    ms.recv_len = engine.mtu
    ms.is_it_a_tcp_server = True
    ms.is_it_a_tcp_client = False
    ms.cb_tcp_connect = cb_tcp_connect
    ms.cb_tcp_condrop = cb_tcp_condrop
    ms.cb_tcp_recv = cb_tcp_recv
    log('// cb_connect %s'%(ms.cb_tcp_connect.__doc__))
    return ms

def metasock_create_broadcast_sender(engine, mempool, sid, addr, port):
    log('metasock_create_broadcast_sender %s (%s:%s)'%(sid, addr, port))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  
    sock.connect((addr, port))
    #
    ms = Metasock(
        engine=engine,
        mempool=mempool,
        sid=sid,
        addr=addr,
        port=port)
    ms.sock = sock
    ms.can_it_recv = False
    ms.can_it_send = True
    ms.is_it_a_tcp_server = False
    ms.is_it_a_tcp_client = False
    return ms

def metasock_create_tcp_client(engine, mempool, sid, addr, port, cb_tcp_connect, cb_tcp_condrop, cb_tcp_recv):
    log('metasock_create_tcp_client %s (%s:%s)'%(sid, addr, port))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(0)
    sock.connect_ex( (addr, port) )
    #
    ms = Metasock(
        engine=engine,
        mempool=mempool,
        sid=sid,
        addr=addr,
        port=port)
    ms.sock = sock
    ms.can_it_recv = True
    ms.can_it_send = True
    ms.recv_len = engine.mtu
    ms.is_it_a_tcp_server = False
    ms.is_it_a_tcp_client = True
    ms.is_tcp_client_connecting = True
    ms.cb_tcp_connect = cb_tcp_connect
    ms.cb_tcp_condrop = cb_tcp_condrop
    ms.cb_tcp_recv = cb_tcp_recv
    return ms

def metasock_create_accepted_tcp_client(engine, mempool, sid, csock, addr, port, cb_tcp_condrop, cb_tcp_recv, cb_ms_close):
    """This is in the chain of functions that get called after a tcp
    server accepts a client connection."""
    log('metasock_create_accepted_tcp_client %s (%s:%s)'%(sid, addr, port))
    ms = Metasock(
        engine=engine,
        mempool=mempool,
        sid=sid,
        addr=addr,
        port=port)
    ms.sock = csock
    ms.can_it_recv = True
    ms.can_it_send = True
    ms.recv_len = engine.mtu
    ms.is_it_a_tcp_server = False
    ms.is_it_a_tcp_client = True
    ms.cb_tcp_condrop = cb_tcp_condrop
    ms.cb_tcp_recv = cb_tcp_recv
    ms.cb_ms_close = cb_ms_close
    return ms

