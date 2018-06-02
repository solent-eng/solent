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
# Creates a TCP server. A user can netcat/telnet to this port, and then
# interact with a solent application.

from solent import log
from solent import ns
from solent import parse_line_to_tokens

def tokenise_line(line):
    tokens = parse_line_to_tokens(line)
    return tokens

class RailLineConsole:
    def __init__(self):
        self.cs_line_console_connect = ns()
        self.cs_line_console_condrop = ns()
        self.cs_line_console_command = ns()
    def call_line_console_connect(self, rail_h, addr, port):
        self.cs_line_console_connect.rail_h = rail_h
        self.cs_line_console_connect.addr = addr
        self.cs_line_console_connect.port = port
        self.cb_line_console_connect(
            cs_line_console_connect=self.cs_line_console_connect)
    def call_line_console_condrop(self, rail_h, msg):
        self.cs_line_console_condrop.rail_h = rail_h
        self.cs_line_console_condrop.msg = msg
        self.cb_line_console_condrop(
            cs_line_console_condrop=self.cs_line_console_condrop)
    def call_line_console_command(self, rail_h, tokens):
        self.cs_line_console_command.rail_h = rail_h
        self.cs_line_console_command.tokens = tokens
        self.cb_line_console_command(
            cs_line_console_command=self.cs_line_console_command)
    def zero(self, rail_h, cb_line_console_connect, cb_line_console_condrop, cb_line_console_command, engine):
        self.rail_h = rail_h
        self.cb_line_console_connect = cb_line_console_connect
        self.cb_line_console_condrop = cb_line_console_condrop
        self.cb_line_console_command = cb_line_console_command
        self.engine = engine
        #
        self.b_active = False
        self.ip = None
        self.port = None
        self.server_sid = None
        self.accept_sid = None
        self.c_buffer = []
    #
    def eng_turn(self, activity):
        "Returns a boolean which is True only if there was activity."
        pass
    def eng_close(self):
        self.close_everything()
    #
    def start(self, ip, port):
        if self.b_active == True:
            log('ERROR: SpinLineConsole is already active.')
            return
        #
        self.ip = ip
        self.port = port
        #
        self.b_active = True
        self.start_server()
    def stop(self):
        self.b_active = False
        self.close_everything()
    def send(self, msg):
        if not self.accept_sid:
            raise Exception('Not valid to call this with None client sid.')
        bb = bytes(
            source=msg,
            encoding='utf8')
        self.engine.send(
            sid=self.accept_sid,
            bb=bb)
    #
    def _boot_any_accept(self):
        if self.accept_sid != None:
            self.engine.close_tcp_accept(
                accept_sid=self.accept_sid)
    def _boot_any_server(self):
        if self.server_sid != None:
            self.engine.close_tcp_server(
                server_sid=self.server_sid)
    def cb_tcp_server_start(self, cs_tcp_server_start):
        engine = cs_tcp_server_start.engine
        server_sid = cs_tcp_server_start.server_sid
        addr = cs_tcp_server_start.addr
        port = cs_tcp_server_start.port
        #
        self.server_sid = server_sid
    def cb_tcp_server_stop(self, cs_tcp_server_stop):
        engine = cs_tcp_server_stop.engine
        server_sid = cs_tcp_server_stop.server_sid
        message = cs_tcp_server_stop.message
        #
        self.server_sid = None
    def cb_tcp_accept_connect(self, cs_tcp_accept_connect):
        engine = cs_tcp_accept_connect.engine
        server_sid = cs_tcp_accept_connect.server_sid
        accept_sid = cs_tcp_accept_connect.accept_sid
        accept_addr = cs_tcp_accept_connect.accept_addr
        accept_port = cs_tcp_accept_connect.accept_port
        #
        self._boot_any_server()
        self.accept_sid = accept_sid
        self.c_buffer = []
        self.call_line_console_connect(
            rail_h=self.rail_h,
            addr=accept_addr,
            port=accept_port)
    def cb_tcp_accept_condrop(self, cs_tcp_accept_condrop):
        engine = cs_tcp_accept_condrop.engine
        accept_sid = cs_tcp_accept_condrop.accept_sid
        message = cs_tcp_accept_condrop.message
        #
        self.accept_sid = None
        self.call_line_console_condrop(
            rail_h=self.rail_h,
            msg=message)
        if self.b_active:
            self.start_server()
    def cb_tcp_accept_recv(self, cs_tcp_accept_recv):
        engine = cs_tcp_accept_recv.engine
        accept_sid = cs_tcp_accept_recv.accept_sid
        bb = cs_tcp_accept_recv.bb
        #
        try:
            s = bb.decode('utf8')
        except UnicodeDecodeError as e:
            hexdump(bb)
            log('ERROR: unicode decode error. |%s|'%(accept_sid))
            engine.close_tcp_accept(
                accept_sid=accept_sid)
            return
        #
        for c in s:
            if c == '\n':
                line = ''.join(self.c_buffer)
                self.c_buffer = []
                tokens = tokenise_line(
                    line=line)
                self.call_line_console_command(
                    rail_h=self.rail_h,
                    tokens=tokens)
            elif c == '\r':
                continue
            else:
                self.c_buffer.append(c)
    #
    def close_everything(self):
        self._boot_any_accept()
        self._boot_any_server()
    def start_server(self):
        self.engine.open_tcp_server(
            addr=self.ip,
            port=self.port,
            cb_tcp_server_start=self.cb_tcp_server_start,
            cb_tcp_server_stop=self.cb_tcp_server_stop,
            cb_tcp_accept_connect=self.cb_tcp_accept_connect,
            cb_tcp_accept_condrop=self.cb_tcp_accept_condrop,
            cb_tcp_accept_recv=self.cb_tcp_accept_recv)
    def is_server_listening(self):
        return self.server_sid != None
    def is_accept_connected(self):
        return self.accept_sid != None

