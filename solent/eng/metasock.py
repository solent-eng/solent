#
# metasock
#
# // overview
# Unless you are working on the engine, you should never need to look at
# this class. (Nor would you want to.)
#
# If you press on, start with the pydoc for the Metasock class below.
#
# Here and in engine, you'll find laboriously detailed notes about
# implementation. Usually this is something to avoid. Comments that annotate
# implementation make code brittle. Comments that describe the implementation
# of other parts of the codebase are much worse. But this settlement is not an
# accident.
#
#   a verbose defense of all the verbose commenting
#   ========================================================
#   This class + engine are attempting a difficult task: producing a clean
#   facade around the Berkeley sockets API. The nastiness has caused me to
#   intertwine these two classes in a manner that goes far beyond what is
#   desirable in typical OO code. The comments seek to highlight the
#   intertwined section, and to explain weird sections by highlighting the
#   Berkeley API pitfalls that overcome.
#
#   As a general rule, heavy documentation is an obstacle to someone who
#   wanted to change code, and creates maintenance risk. But in this case,
#   heavy documentation is justified.
#
#   Generally, code should be written to be maintained. In this case, the
#   detail of comments help more than they hurt.
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

from .cs import CsPubStart
from .cs import CsPubStop
from .cs import CsSubStart
from .cs import CsSubStop
from .cs import CsSubRecv
from .cs import CsTcpClientCondrop
from .cs import CsTcpClientConnect
from .cs import CsTcpClientRecv
from .cs import CsTcpAcceptCondrop
from .cs import CsTcpAcceptConnect
from .cs import CsTcpAcceptRecv
from .cs import CsTcpServerStart
from .cs import CsTcpServerStop

from solent.log import hexdump_bytes
from solent.log import log

from collections import deque
import errno
import socket
import traceback

def l_cb_error(cb_struct):
    def fn(**args):
        raise Exception(cb_struct)
    return fn

class MetasockCloseCondition(Exception):
    def __init__(self, message):
        self.message = message

MS_TYPE_TCP_ACCEPT = 'tcp_accept'
MS_TYPE_TCP_CLIENT = 'tcp_client'
MS_TYPE_TCP_SERVER = 'tcp_server'
MS_TYPE_PUB = 'pub'
MS_TYPE_SUB = 'sub'

class Metasock(object):
    """This is a mechanism for creating a socket with intent.
    
    // Huh?

    Let's talk about the problem this solves.
    
    The functions that create a unix socket offer no obvious way to indicate
    details about it that are useful in practice. For example, whether you
    intend for it to be read from or written to. So, we have to maintain that
    information separately.
    
    An instance of this class tracks whether you want for it to be read from
    or written to. This information will be used for contructing a select call
    on the fly, and for appropriately managing a socket when it is market as
    ready-for-action by the return from select().

    // Anything else?

    This uses callbacks. That means that the select loop can work
    like this: (1) identify all the metasockets that need reading from and
    writing to; (2) carry around a surgical select on that basis; (3) lookup
    the metasocket that corresponds to the sockets you get back from the
    select. (4) call read / write on them as appropriate. For recv, the
    metasocket can just funnel any content it gets to its callbacks
    """
    def __init__(self, engine, mempool, sid, ms_type, addr, port):
        self.engine = engine
        self.mempool = mempool
        self.sid = sid
        self.ms_type = ms_type
        self.addr = addr
        self.port = port
        #
        self.sock = None
        self.parent_sid = None
        #
        self.can_it_recv = False
        self.recv_len = engine.mtu
        #
        self.can_it_send = False
        self.send_buf = deque() # buffers sips
        #
        self.b_tcp_client_connecting = False
        #
        self.cb_pub_start = l_cb_error('cb_pub_start not set')
        self.cs_pub_start = CsPubStart()
        self.cb_pub_stop = l_cb_error('cb_pub_stop not set')
        self.cs_pub_stop = CsPubStop()
        self.cb_sub_start = l_cb_error('cb_pub_start not set')
        self.cs_sub_start = CsSubStart()
        self.cb_sub_stop = l_cb_error('cb_pub_stop not set')
        self.cs_sub_stop = CsSubStop()
        self.cb_sub_recv = l_cb_error('cb_sub_recv not set')
        self.cs_sub_recv = CsSubRecv()
        self.cb_tcp_accept_recv = l_cb_error('cb_tcp_accept_recv not set')
        self.cs_tcp_accept_recv = CsTcpAcceptRecv()
        self.cb_tcp_accept_connect = l_cb_error('cb_tcp_accept_connect not set')
        self.cs_tcp_accept_connect = CsTcpAcceptConnect()
        self.cb_tcp_accept_condrop = l_cb_error('cb_tcp_accept_condrop not set')
        self.cs_tcp_accept_condrop = CsTcpAcceptCondrop()
        self.cb_tcp_client_connect = l_cb_error('cb_tcp_client_connect not set')
        self.cs_tcp_client_connect = CsTcpClientConnect()
        self.cb_tcp_client_condrop = l_cb_error('cb_tcp_client_condrop not set')
        self.cs_tcp_client_condrop = CsTcpClientCondrop()
        self.cb_tcp_client_recv = l_cb_error('cb_tcp_client_recv not set')
        self.cs_tcp_client_recv = CsTcpClientRecv()
        self.cb_tcp_server_start = l_cb_error('cb_tcp_server_start not set')
        self.cs_tcp_server_start = CsTcpServerStart()
        self.cb_tcp_server_stop = l_cb_error('cb_tcp_server_stop not set')
        self.cs_tcp_server_stop = CsTcpServerStop()
    def after_init(self):
        '''This gets called after the factory function has finished setting up
        the instance to its taste. In practice, it's useful for sending
        callbacks to metasock types that require it.'''
        if self.ms_type == MS_TYPE_PUB:
            self.cs_pub_start.engine = self.engine
            self.cs_pub_start.pub_sid = self.sid
            self.cs_pub_start.addr = self.addr
            self.cs_pub_start.port = self.port
            self.cb_pub_start(
                cs_pub_start=self.cs_pub_start)
        elif self.ms_type == MS_TYPE_SUB:
            self.cs_sub_start.engine = self.engine
            self.cs_sub_start.sub_sid = self.sid
            self.cs_sub_start.addr = self.addr
            self.cs_sub_start.port = self.port
            self.cb_sub_start(
                cs_sub_start=self.cs_sub_start)
        elif self.ms_type == MS_TYPE_TCP_ACCEPT:
            self.cs_tcp_accept_connect.engine = self.engine
            self.cs_tcp_accept_connect.server_sid = self.parent_sid
            self.cs_tcp_accept_connect.accept_sid = self.sid
            self.cs_tcp_accept_connect.client_addr = self.addr
            self.cs_tcp_accept_connect.client_port = self.port
            self.cb_tcp_accept_connect(
                cs_tcp_accept_connect=self.cs_tcp_accept_connect)
        elif self.ms_type == MS_TYPE_TCP_CLIENT:
            # We're not interested in a callback from a client after creation.
            # As a client, the significant stop is once we have successfully
            # negotiated a tcp connection to the other side. That logic is
            # handled in [ms_successful_connection_as_tcp_client].
            pass
        elif self.ms_type == MS_TYPE_TCP_SERVER:
            self.cs_tcp_server_start.engine = self.engine
            self.cs_tcp_server_start.server_sid = self.sid
            self.cs_tcp_server_start.addr = self.addr
            self.cs_tcp_server_start.port = self.port
            self.cb_tcp_server_start(
                cs_tcp_server_start=self.cs_tcp_server_start)
        else:
            raise Exception('Algorithm exception. [%s]'%(self.ms_type))
    def close(self, message):
        '''
        Safely attempts to close the socket. This should be called from one
        place and one place only - engine._close_metasock. (It's tightly
        coupled into the way the select loop runs.)
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
        if self.ms_type == MS_TYPE_PUB:
            self.cs_pub_stop.engine = self.engine
            self.cs_pub_stop.pub_sid = self.sid
            self.cs_pub_stop.message = message
            self.cb_pub_stop(
                cs_pub_stop=self.cs_pub_stop)
        elif self.ms_type == MS_TYPE_SUB:
            self.cs_sub_stop.engine = self.engine
            self.cs_sub_stop.sub_sid = self.sid
            self.cs_sub_stop.message = message
            self.cb_sub_stop(
                cs_sub_stop=self.cs_sub_stop)
        elif self.ms_type == MS_TYPE_TCP_ACCEPT:
            self.cs_tcp_accept_condrop.engine = self.engine
            self.cs_tcp_accept_condrop.server_sid = self.parent_sid
            self.cs_tcp_accept_condrop.accept_sid = self.sid
            self.cs_tcp_accept_condrop.message = message
            self.cb_tcp_accept_condrop(
                cs_tcp_accept_condrop=self.cs_tcp_accept_condrop)
        elif self.ms_type == MS_TYPE_TCP_CLIENT:
            self.cs_tcp_client_condrop.engine = self.engine
            self.cs_tcp_client_condrop.client_sid = self.sid
            self.cs_tcp_client_condrop.message = message
            self.cb_tcp_client_condrop(
                cs_tcp_client_condrop=self.cs_tcp_client_condrop)
        elif self.ms_type == MS_TYPE_TCP_SERVER:
            self.cs_tcp_server_stop.engine = self.engine
            self.cs_tcp_server_stop.server_sid = self.sid
            self.cs_tcp_server_stop.message = message
            self.cb_tcp_server_stop(
                cs_tcp_server_stop=self.cs_tcp_server_stop)
        else:
            raise Exception('Algorithm exception. [%s]'%(self.ms_type))
    def desire_for_readable_select_list(self):
        if self.b_tcp_client_connecting:
            # (Because the process of connecting is handled out of the writable
            # select list.)
            return False
        if self.can_it_recv:
            return True
        return False
    def desire_for_writable_select_list(self):
        if self.b_tcp_client_connecting:
            return True
        if self.ms_type == MS_TYPE_TCP_SERVER:
            return True
        if self.can_it_send and self.send_buf:
            return True
        return False
    def copy_to_send_queue(self, sip):
        self.send_buf.append(
            self.mempool.clone(sip))
    def manage_exceptionable(self):
        '''
        Managed socket has appeared in xlist in the select. At some point we
        will be closing it, but over time we will probably want to add logic
        that inspects the socket in order to give more helpful messages.
        '''
        raise MetasockCloseCondition('select/xlist')
    def manage_readable(self):
        '''
        When select marks a socket as readable, it implies one of these
        scenarios:
        * Server socket has a pending inbound connection needing an accept
        * There's data in a socket's inbound queue, waiting to be read
        * Sudden client disconnect
        '''
        #
        # In Berkeley sockets, an indication that a server socket is
        # ready-to-read means something completely different to an indication
        # that a client socket is ready-to-read. Here we split these
        # behaviours into different codepaths.
        #
        # // server socket codepath
        if self.ms_type == MS_TYPE_TCP_SERVER:
            (accept_sock, (addr, port)) = self.sock.accept()
            self.engine.register_tcp_accept(
                accept_sock=accept_sock,
                addr=addr,
                port=port,
                parent_sid=self.sid,
                cb_tcp_accept_connect=self.cb_tcp_accept_connect,
                cb_tcp_accept_condrop=self.cb_tcp_accept_condrop,
                cb_tcp_accept_recv=self.cb_tcp_accept_recv)
            return
        #
        # // non-server socket codepath
        try:
            bb = self.sock.recv(self.recv_len)
        except Exception as e:
            # If you're going to disappear errors here, do it with an
            # exception that is specific to a real read_fail. Note,
            # * You can't count on e.message existing
            # * Ugly string comparison might be the only way to do it
            log('recv exception [sid %s] [%s]'%(self.sid, str(e)))
            raise MetasockCloseCondition('read_fail')
            return
        if bb in (None,) or 0 == len(bb):
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
        if self.ms_type == MS_TYPE_PUB:
            raise Exception("This port should never recv.")
        elif self.ms_type == MS_TYPE_SUB:
            self.cs_sub_recv.engine = self.engine
            self.cs_sub_recv.sub_sid = self.sid
            self.cs_sub_recv.bb = bb
            self.cb_sub_recv(
                cs_sub_recv=self.cs_sub_recv)
        elif self.ms_type == MS_TYPE_TCP_ACCEPT:
            #hexdump_bytes(
            #    arr=bb,
            #    title='** metasock client read**')
            self.cs_tcp_accept_recv.engine = self.engine
            self.cs_tcp_accept_recv.accept_sid = self.sid
            self.cs_tcp_accept_recv.bb = bb
            self.cb_tcp_accept_recv(
                cs_tcp_accept_recv=self.cs_tcp_accept_recv)
        elif self.ms_type == MS_TYPE_TCP_CLIENT:
            #hexdump_bytes(
            #    arr=bb,
            #    title='** metasock client read**')
            self.cs_tcp_client_recv.engine = self.engine
            self.cs_tcp_client_recv.client_sid = self.sid
            self.cs_tcp_client_recv.bb = bb
            self.cb_tcp_client_recv(
                cs_tcp_client_recv=self.cs_tcp_client_recv)
        elif self.ms_type == MS_TYPE_TCP_SERVER:
            raise Exception("Should not get here.")
        else:
            raise Exception("Algorithm exception [%s]"%(self.ms_type))
    def manage_writable(self):
        '''
        When select marks a socket as writable, it implies one of these
        scenarios:
        * Client sockets in the process of connecting
        * Sockets which can be written to
        * Sudden client disconnect
        '''
        if not self.can_it_send:
            raise Exception("%s is not a send sock."%self.sid)
        if self.b_tcp_client_connecting:
            ec = self.sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            log('b_tcp_client_connecting %s'%ec)
            if 0 == ec:
                # :ms_successful_connection_as_tcp_client
                self.b_tcp_client_connecting = False
                self.cs_tcp_client_connect.engine = self.engine
                self.cs_tcp_client_connect.client_sid = self.sid
                self.cs_tcp_client_connect.addr = self.addr
                self.cs_tcp_client_connect.port = self.port
                self.cb_tcp_client_connect(
                    cs_tcp_client_connect=self.cs_tcp_client_connect)
            elif 'EINPROGRESS' == errno.errorcode[ec]:
                pass
            else:
                e_message = errno.errorcode[ec]
                r = ' '.join( [ 'Unable to connect to'
                              , '%s:%s'%(self.addr, self.port)
                              , '[%s:%s]'%(ec, e_message)
                              ] )
                raise MetasockCloseCondition(r)
            return
        try:
            while self.send_buf:
                sip = self.send_buf.popleft()
                bb = sip.get()
                send_size = self.sock.send(bb)
                if send_size == len(bb):
                    # Ideal situation: our send was successful
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
                    # This is weird. Since our bb must be smaller than
                    # the MTU size, this should never happen.
                    raise Algorithm("Weird: partial payload send. %s of %s"%(
                        send_size, len(bb)))
        except:
            # When you try to do a send to a BSD socket that is in the
            # process of going down, you can get an exception. This caterss
            # for that scenario.
            raise MetasockCloseCondition('send_fail')
            return

def sock_nodelay_condition(engine, sock):
    if engine.b_nodelay:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

def metasock_create_pub(engine, mempool, sid, addr, port, cb_pub_start, cb_pub_stop):
    log('metasock_create_pub %s (%s:%s)'%(sid, addr, port))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
    sock_nodelay_condition(
        engine=engine,
        sock=sock)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  
    sock.connect((addr, port))
    #
    ms = Metasock(
        engine=engine,
        mempool=mempool,
        sid=sid,
        ms_type=MS_TYPE_PUB,
        addr=addr,
        port=port)
    ms.sock = sock
    ms.can_it_recv = False
    ms.can_it_send = True
    ms.cb_pub_start = cb_pub_start
    ms.cb_pub_stop = cb_pub_stop
    #
    engine._map_sid_to_metasock(
        sid=sid,
        ms=ms)
    ms.after_init()
    #
    return ms

def metasock_create_sub(engine, mempool, sid, addr, port, cb_sub_start, cb_sub_stop, cb_sub_recv):
    log('metasock_create_sub %s (%s:%s)'%(sid, addr, port))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_nodelay_condition(
        engine=engine,
        sock=sock)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((addr, port))
    sock.setblocking(0)
    #
    ms = Metasock(
        engine=engine,
        mempool=mempool,
        sid=sid,
        ms_type=MS_TYPE_SUB,
        addr=addr,
        port=port)
    ms.sock = sock
    ms.can_it_recv = True
    ms.can_it_send = False
    ms.cb_sub_start = cb_sub_start
    ms.cb_sub_stop = cb_sub_stop
    ms.cb_sub_recv = cb_sub_recv
    #
    engine._map_sid_to_metasock(
        sid=sid,
        ms=ms)
    ms.after_init()
    #
    return ms

def metasock_create_tcp_accept(engine, mempool, sid, accept_sock, addr, port, parent_sid, cb_tcp_accept_connect, cb_tcp_accept_condrop, cb_tcp_accept_recv):
    """This is in the chain of functions that get called after a tcp server
    accepts a connection. In BSD sockets language, this is considered to be a
    'client' socket. But in our language, we call this an 'accept' socket.
    That is, we distinguish between server, client and accept."""
    log('metasock_create_tcp_accept %s (%s:%s)'%(sid, addr, port))
    sock_nodelay_condition(
        engine=engine,
        sock=accept_sock)
    #
    ms = Metasock(
        engine=engine,
        mempool=mempool,
        sid=sid,
        ms_type=MS_TYPE_TCP_ACCEPT,
        addr=addr,
        port=port)
    ms.sock = accept_sock
    ms.can_it_recv = True
    ms.can_it_send = True
    ms.parent_sid = parent_sid
    ms.cb_tcp_accept_connect = cb_tcp_accept_connect
    ms.cb_tcp_accept_condrop = cb_tcp_accept_condrop
    ms.cb_tcp_accept_recv = cb_tcp_accept_recv
    #
    engine._map_sid_to_metasock(
        sid=sid,
        ms=ms)
    ms.after_init()
    #
    return ms

def metasock_create_tcp_client(engine, mempool, sid, addr, port, cb_tcp_client_connect, cb_tcp_client_condrop, cb_tcp_client_recv):
    log('metasock_create_tcp_client %s (%s:%s)'%(sid, addr, port))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_nodelay_condition(
        engine=engine,
        sock=sock)
    sock.setblocking(0)
    sock.connect_ex( (addr, port) )
    #
    ms = Metasock(
        engine=engine,
        mempool=mempool,
        sid=sid,
        ms_type=MS_TYPE_TCP_CLIENT,
        addr=addr,
        port=port)
    ms.sock = sock
    ms.can_it_recv = True
    ms.can_it_send = True
    ms.b_tcp_client_connecting = True
    ms.cb_tcp_client_connect = cb_tcp_client_connect
    ms.cb_tcp_client_condrop = cb_tcp_client_condrop
    ms.cb_tcp_client_recv = cb_tcp_client_recv
    #
    engine._map_sid_to_metasock(
        sid=sid,
        ms=ms)
    ms.after_init()
    #
    return ms

def metasock_create_tcp_server(engine, mempool, sid, addr, port, cb_tcp_server_start, cb_tcp_server_stop, cb_tcp_accept_connect, cb_tcp_accept_condrop, cb_tcp_accept_recv):
    log('metasock_create_tcp_server %s (%s:%s)'%(sid, addr, port))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_nodelay_condition(
        engine=engine,
        sock=sock)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((addr, port))
    sock.setblocking(0)
    sock.listen(0)
    #
    ms = Metasock(
        engine=engine,
        mempool=mempool,
        sid=sid,
        ms_type=MS_TYPE_TCP_SERVER,
        addr=addr,
        port=port)
    ms.sock = sock
    ms.can_it_recv = True
    ms.can_it_send = True
    ms.cb_tcp_accept_condrop = cb_tcp_accept_condrop
    ms.cb_tcp_accept_connect = cb_tcp_accept_connect
    ms.cb_tcp_accept_recv = cb_tcp_accept_recv
    ms.cb_tcp_server_start = cb_tcp_server_start
    ms.cb_tcp_server_stop = cb_tcp_server_stop
    #
    engine._map_sid_to_metasock(
        sid=sid,
        ms=ms)
    ms.after_init()
    #
    return ms

