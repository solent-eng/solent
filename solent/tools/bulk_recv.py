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
# The motive for these bulk tools is that they give us a means for moving
# files around on hosts with limited tooling and where the user does not
# necessarily have the kind of system-level access.
#
# This module allows you to launch a server. It wlil wait for clients, and
# then dump the binary content they send to a file. The filename is not
# included with the payload.
#
# // issues
# RailRecvBulkProtocol could now be refactored out and replaced by
# solent.util.RailWireDocUnpack

from solent import ns as Ns
from solent import Engine
from solent import log
from solent.util import RailWireStringUnpack

import os
import struct
import sys
import time


# --------------------------------------------------------
#   struct
# --------------------------------------------------------
#
# In bulk protocol, there is an opening packet which contains the payload
# length to be sent.

BULK_MODES = [
    'u8_length',
    'bb_data']

class RailRecvBulkProtocol:

    def __init__(self):
        self.cs_recv_bulk_protocol_head = Ns()
        self.cs_recv_bulk_protocol_data = Ns()
        self.cs_recv_bulk_protocol_done = Ns()

        self.mode = None
        self.doc_len = None
        self.buf = []
        self.got = None

    def call_recv_bulk_protocol_head(self, zero_h, doc_len):
        self.cs_recv_bulk_protocol_head.zero_h = zero_h
        self.cs_recv_bulk_protocol_head.doc_len = doc_len
        self.cb_recv_bulk_protocol_head(
            cs_recv_bulk_protocol_head=self.cs_recv_bulk_protocol_head)

    def call_recv_bulk_protocol_data(self, zero_h, bb):
        self.cs_recv_bulk_protocol_data.zero_h = zero_h
        self.cs_recv_bulk_protocol_data.bb = bb
        self.cb_recv_bulk_protocol_data(
            cs_recv_bulk_protocol_data=self.cs_recv_bulk_protocol_data)

    def call_recv_bulk_protocol_done(self, zero_h):
        self.cs_recv_bulk_protocol_done.zero_h = zero_h
        self.cb_recv_bulk_protocol_done(
            cs_recv_bulk_protocol_done=self.cs_recv_bulk_protocol_done)

    def zero(self, zero_h, cb_recv_bulk_protocol_head, cb_recv_bulk_protocol_data, cb_recv_bulk_protocol_done, block_size):
        self.zero_h = zero_h
        self.cb_recv_bulk_protocol_head = cb_recv_bulk_protocol_head
        self.cb_recv_bulk_protocol_data = cb_recv_bulk_protocol_data
        self.cb_recv_bulk_protocol_done = cb_recv_bulk_protocol_done
        self.block_size = block_size

        self.mode = 0
        self.doc_len = None
        self.buf.clear()
        self.got = 0

    def accept(self, bb):
        bb_idx = 0

        if self.mode > 1:
            log("WARNING: have already sent cb_recv_bulk_protocol_done.")
            return

        while self.mode == 0:
            if bb_idx >= len(bb):
                return bb_idx

            self.buf.append(bb[bb_idx])
            bb_idx += 1

            if 8 == len(self.buf):
                self.doc_len = struct.unpack_from(
                    '!Q', 
                    bytes(self.buf),
                    0)[0]
                self.mode = 1
                self.buf.clear()

                self.call_recv_bulk_protocol_head(
                    zero_h=self.zero_h,
                    doc_len=self.doc_len)

        while self.mode == 1:
            if bb_idx >= len(bb):
                return bb_idx

            self.buf.append(bb[bb_idx])
            bb_idx += 1

            blen = len(self.buf)
            if self.got + blen >= self.doc_len:
                # send what is left, and close things out.
                bb_send = bytes(self.buf)
                self.buf.clear()

                self.got += blen

                self.call_recv_bulk_protocol_data(
                    zero_h=self.zero_h,
                    bb=bb_send)

                self.call_recv_bulk_protocol_done(
                    zero_h=self.zero_h)

                self.mode = 2

            elif blen == self.block_size:
                # send an intermediate block
                bb_send = bytes(self.buf)
                self.buf.clear()

                self.got += blen

                self.call_recv_bulk_protocol_data(
                    zero_h=self.zero_h,
                    bb=bb_send)


# --------------------------------------------------------
#   model
# --------------------------------------------------------
I_NEARCAST = '''
    i message h
    i field h

    message prime_server
        field bulk_addr
        field bulk_port
        field dir_save
    message init

    message head
        field blen
    message data
        field bb
    message tail
'''

class TrackPrime:

    def __init__(self, orb):
        self.orb = orb

    def on_prime_server(self, bulk_addr, bulk_port, dir_save):
        self.bulk_addr = bulk_addr
        self.bulk_port = bulk_port
        self.dir_save = dir_save

class CogNetwork:

    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine

        self.track_prime = self.orb.track(TrackPrime)

        self.server_sid = None
        self.accept_sid = None

        self.path = None
        self.f_ptr = None
        self.doc_len = None
        self.doc_so_far = 0

        self.rail_recv_bulk_protocol = RailRecvBulkProtocol()

    def __start_server(self):
        self.server_sid = self.engine.open_tcp_server(
            addr=self.track_prime.bulk_addr,
            port=self.track_prime.bulk_port,
            cb_tcp_server_start=self.cb_tcp_server_start,
            cb_tcp_server_stop=self.cb_tcp_server_stop,
            cb_tcp_accept_connect=self.cb_tcp_accept_connect,
            cb_tcp_accept_condrop=self.cb_tcp_accept_condrop,
            cb_tcp_accept_recv=self.cb_tcp_accept_recv)

    def __stop_server(self):
        self.engine.close_tcp_server(
            server_sid=self.server_sid)

    def on_init(self):
        self.__start_server()

    def cb_tcp_server_start(self, cs_tcp_server_start):
        engine = cs_tcp_server_start.engine
        server_sid = cs_tcp_server_start.server_sid
        addr = cs_tcp_server_start.addr
        port = cs_tcp_server_start.port

        pass

    def cb_tcp_server_stop(self, cs_tcp_server_stop):
        engine = cs_tcp_server_stop.engine
        server_sid = cs_tcp_server_stop.server_sid
        msg = cs_tcp_server_stop.message

        pass

    def cb_tcp_accept_connect(self, cs_tcp_accept_connect):
        engine = cs_tcp_accept_connect.engine
        server_sid = cs_tcp_accept_connect.server_sid
        accept_sid = cs_tcp_accept_connect.accept_sid
        accept_addr = cs_tcp_accept_connect.accept_addr
        accept_port = cs_tcp_accept_connect.accept_port

        self.__stop_server()

        self.accept_sid = accept_sid

        fingerprint = '%s.%s.%s'%(server_sid, accept_addr, accept_port)
        log('[tcp accept connect, %s]'%(fingerprint))

        kilobyte = 1024
        megabyte = kilobyte * 1024

        block_size = megabyte
        zero_h = fingerprint
        self.rail_recv_bulk_protocol.zero(
            zero_h=zero_h,
            cb_recv_bulk_protocol_head=self.cb_recv_bulk_protocol_head,
            cb_recv_bulk_protocol_data=self.cb_recv_bulk_protocol_data,
            cb_recv_bulk_protocol_done=self.cb_recv_bulk_protocol_done,
            block_size=block_size)

        now = time.strftime('%s')
        self.path = os.path.join(
            self.track_prime.dir_save,
            '%s.%s.bin'%(now, fingerprint))

        self.f_ptr = open(self.path, 'wb+')

    def cb_tcp_accept_condrop(self, cs_tcp_accept_condrop):
        engine = cs_tcp_accept_condrop.engine
        server_sid = cs_tcp_accept_condrop.server_sid
        accept_sid = cs_tcp_accept_condrop.accept_sid

        log('[tcp accept condrop]')

        self.f_ptr.close()

        self.__start_server()

    def cb_tcp_accept_recv(self, cs_tcp_accept_recv):
        engine = cs_tcp_accept_recv.engine
        accept_sid = cs_tcp_accept_recv.accept_sid
        bb = cs_tcp_accept_recv.bb

        self.rail_recv_bulk_protocol.accept(bb)

    def cb_recv_bulk_protocol_head(self, cs_recv_bulk_protocol_head):
        zero_h = cs_recv_bulk_protocol_head.zero_h
        doc_len = cs_recv_bulk_protocol_head.doc_len

        self.doc_len = doc_len
        self.doc_so_far = 0
        log(
            'bulk head: %s, doc length: %s'%(
                zero_h, doc_len))

    def cb_recv_bulk_protocol_data(self, cs_recv_bulk_protocol_data):
        zero_h = cs_recv_bulk_protocol_data.zero_h
        bb = cs_recv_bulk_protocol_data.bb

        self.doc_so_far += len(bb)
        log(
            'bulk data: %s, block length (%s of %s)'%(
                zero_h, self.doc_so_far, self.doc_len))

        self.f_ptr.write(bb)

    def cb_recv_bulk_protocol_done(self, cs_recv_bulk_protocol_done):
        zero_h = cs_recv_bulk_protocol_done.zero_h

        log('bulk data: %s, doc done'%(zero_h))

        self.f_ptr.close()

        self.engine.close_tcp_accept(
            accept_sid=self.accept_sid)

def init_nearcast(engine, bulk_addr, bulk_port, dir_save):
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST)
    orb.init_cog(CogNetwork)
    orb.add_log_snoop()

    bridge = orb.init_autobridge()
    bridge.nearcast.prime_server(
        bulk_addr=bulk_addr,
        bulk_port=bulk_port,
        dir_save=dir_save)
    bridge.nearcast.init()

    return bridge


# --------------------------------------------------------
#   launch
# --------------------------------------------------------
MTU = 1500

def main():
    (_cmd, dir_save, bulk_addr, bulk_port) = sys.argv
    bulk_port = int(bulk_port)

    if not os.path.exists(dir_save):
        raise Exception("No dir at %s"%(dir_save))
    if not os.path.isdir(dir_save):
        raise Exception("Path at %s is not a directory."%(dir_save))

    engine = Engine(
        mtu=MTU)
    try:
        bridge = init_nearcast(
            engine=engine,
            bulk_addr=bulk_addr,
            bulk_port=bulk_port,
            dir_save=dir_save)
        engine.event_loop()
    finally:
        engine.close()

if __name__ == '__main__':
    main()


