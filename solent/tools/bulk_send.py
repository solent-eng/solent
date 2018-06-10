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
# This dispatches binary files towards a bulk_recv server. When you start it
# up, you need to name an address and port to target. But it does not connect
# immediately. Rather, you telnet to the line console in this bulk receive
# process (see CONS_ADDR, CONS_PORT). For each filename you name in the
# console, this service will make a connection to the target ip and port, and
# attempt to make an upload.

from solent import Engine
from solent import log
from solent.util import RailLineConsole

from collections import deque
import os
import sys
import struct


# --------------------------------------------------------
#   model
# --------------------------------------------------------
I_NEARCAST = '''
    i message h
    i field h

    message prime_server
        field bulk_addr
        field bulk_port
    message prime_console
        field cons_addr
        field cons_port
    message init

    message please_queue_for_send
        field enqueue_h
        field filename
    message failed_queue_for_send
        field enqueue_h
        field msg
    message okdone_queue_for_send
        field enqueue_h
        field filename
'''


class TrackPrime:

    def __init__(self, orb):
        self.orb = orb

    def on_prime_console(self, cons_addr, cons_port):
        self.cons_addr = cons_addr
        self.cons_port = cons_port

    def on_prime_server(self, bulk_addr, bulk_port):
        self.bulk_addr = bulk_addr
        self.bulk_port = bulk_port


class CogLineConsole:

    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine

        self.track_prime = self.orb.track(TrackPrime)

        self.rail_line_console = RailLineConsole()
        self.bulk_send_count = 0

    def on_init(self):
        rail_h = '%s/line_console'%(self.cog_h)
        self.rail_line_console.zero(
            rail_h=rail_h,
            cb_line_console_connect=self.cb_line_console_connect,
            cb_line_console_condrop=self.cb_line_console_condrop,
            cb_line_console_command=self.cb_line_console_command,
            engine=self.engine)

        self.rail_line_console.start(
            ip=self.track_prime.cons_addr,
            port=self.track_prime.cons_port)

    def on_please_queue_for_send(self, enqueue_h, filename):
        self.rail_line_console.send(
            'queued %s (%s)\n'%(
                enqueue_h, filename))

    def on_failed_queue_for_send(self, enqueue_h, msg):
        self.rail_line_console.send(
            'failed %s (%s)\n'%(
                enqueue_h, msg))

    def on_okdone_queue_for_send(self, enqueue_h, filename):
        self.rail_line_console.send(
            'okdone %s (%s)\n'%(
                enqueue_h, filename))

    def cb_line_console_connect(self, cs_line_console_connect):
        addr = cs_line_console_connect.addr
        port = cs_line_console_connect.port

        pass

    def cb_line_console_condrop(self, cs_line_console_condrop):
        msg = cs_line_console_condrop.msg

        pass

    def cb_line_console_command(self, cs_line_console_command):
        tokens = cs_line_console_command.tokens

        if 1 != len(tokens):
            self.rail_line_console.send('error: expected a filename.')
            return

        filename = tokens[0]
        if not os.path.exists(filename):
            self.rail_line_console.send('error: no file %s'%(filename))
            return

        enqueue_h = self.bulk_send_count
        self.bulk_send_count += 1

        self.nearcast.please_queue_for_send(
            enqueue_h=enqueue_h,
            filename=filename)


class CogNetwork:

    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine

        self.track_prime = self.orb.track(TrackPrime)

        self.send_queue = deque()

        self.client_sid = None
        self.active_finished = False
        self.active_tpl = None

    def on_init(self):
        pass

    def on_please_queue_for_send(self, enqueue_h, filename):
        if not os.path.exists(filename):
            msg = "File %s does not exist."%(filename)
            self.nearcast.failed_queue_for_send(
                enqueue_h=enqueue_h,
                msg=msg)
            return

        self.send_queue.append( (enqueue_h, filename) )
        self.__maybe_start_send()

        self.nearcast.okdone_queue_for_send(
            enqueue_h=enqueue_h,
            filename=filename)

    def __maybe_start_send(self):
        if not self.send_queue:
            return
        if self.client_sid != None:
            return

        log("Attempting a send")
        self.active_finished = False
        self.active_tpl = self.send_queue.popleft()

        self.client_sid = self.engine.open_tcp_client(
            addr=self.track_prime.bulk_addr,
            port=self.track_prime.bulk_port,
            cb_tcp_client_connect=self.cb_tcp_client_connect,
            cb_tcp_client_condrop=self.cb_tcp_client_condrop,
            cb_tcp_client_recv=self.cb_tcp_client_recv)

    def cb_tcp_client_connect(self, cs_tcp_client_connect):
        engine = cs_tcp_client_connect.engine
        client_sid = cs_tcp_client_connect.client_sid
        addr = cs_tcp_client_connect.addr
        port = cs_tcp_client_connect.port

        log('[tcp client connect]')

        (enqueue_h, filename) = self.active_tpl

        # For large files, this will jam the event loop. But this process is
        # not doing much else, so I figure that is fine.
        f_ptr = open(filename, 'rb')
        bb_file = f_ptr.read()
        f_ptr.close()

        # In the protocol for this bulk transfer method, the first eight
        # bytes are a uint64 that tell the other side how much data we
        # will be sending.
        leading_uint64 = bytearray(8)
        struct.pack_into('!Q', leading_uint64, 0, len(bb_file))
        self.engine.send(
            sid=client_sid,
            bb=leading_uint64)

        blen = len(bb_file)
        offset = 0
        while True:
            nail = offset
            peri = offset+engine.mtu
            bb = bb_file[nail:peri]

            self.engine.send(
                sid=client_sid,
                bb=bb)
            offset = peri

            if offset >= blen:
                break

        log("Content is queued engine.")

    def cb_tcp_client_condrop(self, cs_tcp_client_condrop):
        engine = cs_tcp_client_condrop.engine
        client_sid = cs_tcp_client_condrop.client_sid
        message = cs_tcp_client_condrop.message

        log('[tcp client condrop]')

        self.client_sid = None

        self.__maybe_start_send()

    def cb_tcp_client_recv(self, cs_tcp_client_recv):
        engine = cs_tcp_client_recv.engine
        client_sid = cs_tcp_client_recv.client_sid
        bb = cs_tcp_client_recv.bb

        # We do not expect to receive any traffic, and we
        # ignore anything we get.
        pass

def init_nearcast(engine, cons_addr, cons_port, bulk_addr, bulk_port):
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST)
    orb.init_cog(CogLineConsole)
    orb.init_cog(CogNetwork)
    orb.add_log_snoop()

    bridge = orb.init_autobridge()
    bridge.nearcast.prime_server(
        bulk_addr=bulk_addr,
        bulk_port=bulk_port)
    bridge.nearcast.prime_console(
        cons_addr=cons_addr,
        cons_port=cons_port)
    bridge.nearcast.init()

    return bridge


# --------------------------------------------------------
#   launch
# --------------------------------------------------------
CONS_ADDR = '127.0.0.1'
CONS_PORT = 7999

MTU = 1500

def main():
    (_cmd, bulk_addr, bulk_port) = sys.argv
    bulk_port = int(bulk_port)

    engine = Engine(
        mtu=MTU)
    try:
        bridge = init_nearcast(
            engine=engine,
            cons_addr=CONS_ADDR,
            cons_port=CONS_PORT,
            bulk_addr=bulk_addr,
            bulk_port=bulk_port)

        engine.event_loop()
    finally:
        engine.close()

if __name__ == '__main__':
    main()

