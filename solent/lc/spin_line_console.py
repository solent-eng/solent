#
# spin_line_console
#
# // overview
# Creates a TCP server. A user can netcat/telnet to this port to give
# commands.
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

from solent.log import log

class SpinLineConsole:
    def __init__(self, engine, cb_line):
        self.engine = engine
        self.cb_line = cb_line
        #
        self.b_active = False
        self.server_ip = None
        self.server_port = None
        self.server_sid = None
        self.client_sid = None
        self.c_buffer = []
    def at_turn(self, activity):
        "Returns a boolean which is True only if there was activity."
        pass
    def start(self, ip, port):
        if self.b_active == True:
            log('ERROR: SpinLineConsole is already active.')
            return
        self.server_ip = ip
        self.server_port = port
        self._start_server()
    def stop(self):
        self._close_any_client()
        self._close_any_server()
    def write_to_client(self, s):
        if not self.client_sid:
            raise Exception('Not valid to call this with None client sid.')
        payload = bytes(
            source=s,
            encoding='utf8')
        self.engine.send(
            sid=self.client_sid,
            payload=payload)
    #
    def _start_server(self):
        self.server_sid = self.engine.open_tcp_server(
            addr=self.server_ip,
            port=self.server_port,
            cb_tcp_connect=self._engine_on_tcp_connect,
            cb_tcp_condrop=self._engine_on_tcp_condrop,
            cb_tcp_recv=self._engine_on_tcp_recv)
    def _close_any_server(self):
        if self.server_sid == None:
            return
        self.engine.close_tcp_server(
            sid=self.server_sid)
        self.server_sid = None
    def _close_any_client(self):
        if self.client_sid == None:
            return
        self.engine.close_tcp_client(
            sid=self.client_sid)
        self.client_sid = None
    #
    def _engine_on_tcp_connect(self, cs_tcp_connect):
        engine = cs_tcp_connect.engine
        client_sid = cs_tcp_connect.client_sid
        addr = cs_tcp_connect.addr
        port = cs_tcp_connect.port
        #
        self._close_any_server()
        self.client_sid = client_sid
        self.c_buffer = []
    def _engine_on_tcp_condrop(self, cs_tcp_condrop):
        engine = cs_tcp_condrop.engine
        client_sid = cs_tcp_condrop.client_sid
        message = cs_tcp_condrop.message
        #
        self.client_sid = None
        self._start_server()
    def _engine_on_tcp_recv(self, cs_tcp_recv):
        engine = cs_tcp_recv.engine
        client_sid = cs_tcp_recv.client_sid
        data = cs_tcp_recv.data
        #
        for b in data:
            c = chr(b)
            if c == '\n':
                line = ''.join(self.c_buffer)
                self.c_buffer = []
                self.cb_line(
                    line=line)
            elif c == '\r':
                continue
            else:
                self.c_buffer.append(c)

def spin_line_console_new(engine, cb_line):
    ob = SpinLineConsole(
        engine=engine,
        cb_line=cb_line)
    return ob

