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
# Hosts a netcat server. Users can connect to it, authenticate, and then use
# it like a console. Supports multiple concurrent users.

from solent import Engine
from solent import log
from solent import Ns
from solent import parse_line_to_tokens

def tokenise_line(line):
    tokens = parse_line_to_tokens(line)
    return tokens

class Session:
    def __init__(self, accept_sid, addr, port):
        self.accept_sid = accept_sid
        self.addr = addr
        self.port = port
        #
        self.b_auth = False
        self.user = None
        self.c_buffer = []

class RailLinetalk:
    def __init__(self):
        self.cs_linetalk_connect = Ns()
        self.cs_linetalk_conauth = Ns()
        self.cs_linetalk_condrop = Ns()
        self.cs_linetalk_command = Ns()
    def call_linetalk_connect(self, zero_h, accept_sid, addr, port):
        self.cs_linetalk_connect.zero_h = zero_h
        self.cs_linetalk_connect.accept_sid = accept_sid
        self.cs_linetalk_connect.addr = addr
        self.cs_linetalk_connect.port = port
        self.cb_linetalk_connect(
            cs_linetalk_connect=self.cs_linetalk_connect)
    def call_linetalk_conauth(self, zero_h, accept_sid, addr, port, user):
        self.cs_linetalk_conauth.zero_h = zero_h
        self.cs_linetalk_conauth.accept_sid = accept_sid
        self.cs_linetalk_conauth.addr = addr
        self.cs_linetalk_conauth.port = port
        self.cs_linetalk_conauth.user = user
        self.cb_linetalk_conauth(
            cs_linetalk_conauth=self.cs_linetalk_conauth)
    def call_linetalk_condrop(self, zero_h, accept_sid, msg):
        self.cs_linetalk_condrop.zero_h = zero_h
        self.cs_linetalk_condrop.accept_sid = accept_sid
        self.cs_linetalk_condrop.msg = msg
        self.cb_linetalk_condrop(
            cs_linetalk_condrop=self.cs_linetalk_condrop)
    def call_linetalk_command(self, zero_h, accept_sid, tokens):
        self.cs_linetalk_command.zero_h = zero_h
        self.cs_linetalk_command.accept_sid = accept_sid
        self.cs_linetalk_command.tokens = tokens
        self.cb_linetalk_command(
            cs_linetalk_command=self.cs_linetalk_command)
    def zero(self, zero_h, cb_linetalk_connect, cb_linetalk_conauth, cb_linetalk_condrop, cb_linetalk_command, engine):
        self.zero_h = zero_h
        self.cb_linetalk_connect = cb_linetalk_connect
        self.cb_linetalk_conauth = cb_linetalk_conauth
        self.cb_linetalk_condrop = cb_linetalk_condrop
        self.cb_linetalk_command = cb_linetalk_command
        self.engine = engine
        #
        self.b_active = False
        self.d_auth = {}
        self.ip = None
        self.port = None
        self.server_sid = None
        self.d_accept = {} # accept_sid vs Session
    #
    def eng_turn(self, activity):
        "Returns a boolean which is True only if there was activity."
        pass
    def eng_close(self):
        self.close_everything()
    #
    def set_login(self, u, p):
        self.d_auth[u] = p
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
    def send(self, accept_sid, msg):
        if accept_sid not in self.d_accept:
            raise Exception('Invalid target')
        bb = bytes(
            source=msg,
            encoding='utf8')
        self.engine.send(
            sid=accept_sid,
            bb=bb)
    #
    def _boot_any_accept(self):
        for session in self.d_accept:
            accept_sid = session.accept_sid
            self.engine.close_tcp_accept(
                accept_sid=accept_sid)
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
        self.d_accept[accept_sid] = Session(
            accept_sid=accept_sid,
            addr=accept_addr,
            port=accept_port)
        self.call_linetalk_connect(
            zero_h=self.zero_h,
            accept_sid=accept_sid,
            addr=accept_addr,
            port=accept_port)
    def cb_tcp_accept_condrop(self, cs_tcp_accept_condrop):
        engine = cs_tcp_accept_condrop.engine
        accept_sid = cs_tcp_accept_condrop.accept_sid
        message = cs_tcp_accept_condrop.message
        #
        del self.d_accept[accept_sid]
        self.call_linetalk_condrop(
            zero_h=self.zero_h,
            accept_sid=accept_sid,
            msg=message)
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
        session = self.d_accept[accept_sid]
        #
        if session.b_auth:
            c_buffer = session.c_buffer
            for c in s:
                if c == '\n':
                    line = ''.join(c_buffer)
                    c_buffer.clear()
                    tokens = tokenise_line(
                        line=line)
                    self.call_linetalk_command(
                        zero_h=self.zero_h,
                        accept_sid=accept_sid,
                        tokens=tokens)
                elif c == '\r':
                    continue
                else:
                    c_buffer.append(c)
        else:
            tokens = s.strip().split(' ')
            if len(tokens) != 2:
                engine.close_tcp_accept(
                    accept_sid=accept_sid)
                return
            (u, p) = tokens
            if u not in self.d_auth:
                engine.close_tcp_accept(
                    accept_sid=accept_sid)
                return
            if self.d_auth[u] != p:
                engine.close_tcp_accept(
                    accept_sid=accept_sid)
                return
            #
            session.b_auth = True
            session.user = u
            #
            self.call_linetalk_conauth(
                zero_h=self.zero_h,
                accept_sid=accept_sid,
                addr=session.addr,
                port=session.port,
                user=session.user)
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

