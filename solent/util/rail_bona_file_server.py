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
# // overview
# Bona File is a very simple file transfer mechanism that runs over TCP. It
# fills a similar role to TFTP in that it is trivial to implement, and
# feature-poor. But, in contrast to TFP it is authenticated, and it runs over
# TCP.
#
# // protocol
# Client initiates TCP connection, server accepts
#
# Client Request
#   uint8               password string length
#   [unsigned char]     password string. do not terminate with 0 or newline.
#   uint8               relpath string length
#   [unsigned char]     relpath value.
#
# Server Success
#   uint8               status. Will be set to 0.
#   Now raw binary data flows. When the file transfer is done, the server
#   will terminate the TCP connection.
#
# Server File-not-found
#   uint8               status. Will be set to 1.
#
# Server Password Fail
#   uint8               status. Will be set to 2
#

from solent.log import log

import struct


# --------------------------------------------------------
#   connection handler
# --------------------------------------------------------
class ImplBfsHandler:
    def __init__(self):
        pass
    def pool_get(self):
        pass
    def pool_put(self):
        pass

class PoolBfsHandler:
    def __init__(self):
        self.stack = []
        self.active = 0
    def get(self):
        if not self.stack:
            self.stack.append(ImplBfsHandler())
        impl_bfs_handler = self.stack.pop()
        impl_bfs_handler.pool_get()
        self.active += 1
        return impl_bfs_handler
    def len(self):
        return len(self.stack)
    def out(self):
        return self.active
    def put(self, impl_bfs_handler):
        self.stack.append(impl_bfs_handler)
        self.active -= 1


# --------------------------------------------------------
#   bona file server
# --------------------------------------------------------
class CsBonaFileServerConnect:
    # Indicates a TCP connection
    def __init__(self):
        self.accept_sid = None
        self.addr = None
        self.port = None

class CsBonaFileServerCondrop:
    # Indicates a TCP condrop
    def __init__(self):
        self.accept_sid = None
        self.msg = None

class CsBonaFileServerFielded:
    # Indicates a 
    def __init__(self):
        self.accept_sid = None
        self.pw = None
        self.relpath = None

class CsBonaFileServerRejected:
    def __init__(self):
        self.accept_sid = None
        self.msg = None

class CsBonaFileServerSending:
    def __init__(self):
        self.accept_sid = None
        self.path = None
        self.msg = None

class RailBonaFileServer:
    def __init__(self):
        self.pool_bfs_handler = PoolBfsHandler()
        self.cs_bona_file_server_connect = CsBonaFileServerConnect()
        self.cs_bona_file_server_condrop = CsBonaFileServerCondrop()
        self.cs_bona_file_server_fielded = CsBonaFileServerFielded()
        self.cs_bona_file_server_rejected = CsBonaFileServerRejected()
        self.cs_bona_file_server_sending = CsBonaFileServerSending()
    def zero(self, engine, cb_bona_file_connect, cb_bona_file_condrop, cb_bona_file_fielded, cb_bona_file_server_rejected, cb_bona_file_server_sending, addr, port, pw, dir_root):
        self.engine = engine
        self.cb_bona_file_server_connect = cb_bona_file_server_connect
        self.cb_bona_file_server_condrop = cb_bona_file_server_condrop
        self.cb_bona_file_server_fielded = cb_bona_file_server_fielded
        self.cb_bona_file_server_rejected = cb_bona_file_server_rejected
        self.cb_bona_file_server_sending = cb_bona_file_server_sending
        self.addr = addr
        self.port = port
        self.pw = pw
        self.dir_root = dir_root
        #
        self.server_sid = self.engine.open_tcp_server(
            addr=self.addr,
            port=self.port,
            cb_tcp_server_start=self.cb_tcp_server_start,
            cb_tcp_server_stop=self.cb_tcp_server_stop,
            cb_tcp_accept_connect=self.cb_tcp_accept_connect,
            cb_tcp_accept_condrop=self.cb_tcp_accept_condrop,
            cb_tcp_accept_recv=self.cb_tcp_accept_recv)
    #
    def cb_tcp_server_start(self, cs_tcp_server_start):
        engine = cs_tcp_server_start.engine
        server_sid = cs_tcp_server_start.server_sid
        addr = cs_tcp_server_start.addr
        port = cs_tcp_server_start.port
        #
        log('xxx')
    def cb_tcp_server_stop(self, cs_tcp_server_stop):
        engine = cs_tcp_server_stop.engine
        server_sid = cs_tcp_server_stop.server_sid
        message = cs_tcp_server_stop.message
        #
        log('xxx')
    def cb_tcp_accept_connect(self, cs_tcp_accept_connect):
        engine = cs_tcp_accept_connect.engine
        server_sid = cs_tcp_accept_connect.server_sid
        accept_sid = cs_tcp_accept_connect.accept_sid
        accept_addr = cs_tcp_accept_connect.accept_addr
        accept_port = cs_tcp_accept_connect.accept_port
        #
        log('xxx')
    def cb_tcp_accept_condrop(self, cs_tcp_accept_condrop):
        engine = cs_tcp_accept_condrop.engine
        server_sid = cs_tcp_accept_condrop.server_sid
        accept_sid = cs_tcp_accept_condrop.accept_sid
        message = cs_tcp_accept_condrop.message
        #
        log('xxx')
    def cb_tcp_accept_recv(self, cs_tcp_accept_recv):
        engine = cs_tcp_accept_recv.engine
        accept_sid = cs_tcp_accept_recv.accept_sid
        bb = cs_tcp_accept_recv.bb
        #
        log('xxx')


