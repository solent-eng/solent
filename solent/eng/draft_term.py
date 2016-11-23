#!/usr/bin/env python3
#
# Draft term
#
# // brief
# Being used to develop a standard terminal using eng.
#
# // deprecated
# This will disappear in time. Don't use it as a dependency.
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

from solent.eng import create_engine
from solent.eng import nearcast_orb_new
from solent.eng import nearcast_schema_new
from solent.eng import nearcast_snoop_new
from solent.log import init_logging
from solent.log import log
from solent.util import line_finder_new

from collections import deque
from collections import OrderedDict as od
import time
import traceback

# xxx
CONSOLE_ADDR = '127.0.0.1'
CONSOLE_PORT = 4099

TERM_LINK_ADDR = '127.0.0.1'
TERM_LINK_PORT = 4100

TAP_ADDR = '127.0.0.1'
TAP_PORT = 4101

EVENT_ADDR = '127.0.0.1'
EVENT_PORT = 4102

I_NEARCAST_SCHEMA = '''
    i message h
    i field h
    
    message something
        field text

    message connect
        field username
        field password
        field notes
'''


# --------------------------------------------------------
#   :cog_gruel_client
# --------------------------------------------------------
class CogGruelClient:
    def __init__(self, cog_h, nearcast_orb, engine, addr, port):
        self.cog_h = cog_h
        self.nearcast_orb = nearcast_orb
        self.engine = engine
        self.addr = addr
        self.port = port
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



# --------------------------------------------------------
#   :cog_console
# --------------------------------------------------------
def parse_command_line(line):
    if 0 == len(line):
        return (None, [])
    if ' ' not in line:
        return (line, [])
    t = [t for t in line.split() if len(t)>0]
    first = t[0]
    rest = t[1:]
    return (first, rest)

class ModestInterpreter:
    def __init__(self, cog_console):
        self.cog_console = cog_console
    def clear(self):
        pass
    def on_line(self, line):
        log('on_line %s'%(line))
        (head, rest) = parse_command_line(
            line=line)
        if head == None:
            return
        elif head == 'connect':
            self.cog_console.mi_nearcast_connect()
        else:
            self.cog_console.mi_network_write(
                m='error, no command %s'%(head))

def moderst_interpreter_new(cog_console):
    ob = ModestInterpreter(
        cog_console=cog_console)
    return ob

class CogConsole:
    def __init__(self, cog_h, nearcast_orb, engine, addr, port):
        self.cog_h = cog_h
        self.nearcast_orb = nearcast_orb
        self.engine = engine
        self.addr = addr
        self.port = port
        #
        self.modest_interpreter = moderst_interpreter_new(
            cog_console=self)
        self.line_finder = line_finder_new(
            cb_line=self.modest_interpreter.on_line)
        #
        self.server_sid = None
        self.client_sid = None
        self._open_server()
    def close(self):
        self._close_server()
    def at_turn(self):
        "Returns a boolean which is True only if there was activity."
        activity = False
        return activity
    #
    def _open_server(self):
        self.server_sid = self.engine.open_tcp_server(
            addr=self.addr,
            port=self.port,
            cb_tcp_connect=self.engine_on_tcp_connect,
            cb_tcp_confail=self.engine_on_tcp_confail,
            cb_tcp_recv=self.engine_on_tcp_recv)
    def _close_server(self):
        self.engine.close_tcp_server(
            sid=self.server_sid)
        self.server_sid = None
    def _register_client(self, client_sid):
        self.client_sid = client_sid
        #
        self.line_finder.clear()
        self.modest_interpreter.clear()
    #
    def engine_on_tcp_connect(self, cs_tcp_connect):
        engine = cs_tcp_connect.engine
        client_sid = cs_tcp_connect.client_sid
        addr = cs_tcp_connect.addr
        port = cs_tcp_connect.port
        #
        self._close_server()
        self._register_client(
            client_sid=client_sid)
        #
        log("connect/[snoop]/%s/%s/%s"%(
            client_sid,
            addr,
            port))
    def engine_on_tcp_confail(self, cs_tcp_confail):
        engine = cs_tcp_confail.engine
        client_sid = cs_tcp_confail.client_sid
        message = cs_tcp_confail.message
        #
        log("confail/[snoop]/%s/%s"%(client_sid, message))
        self.client_sid = None
        self._open_server()
    def engine_on_tcp_recv(self, cs_tcp_recv):
        engine = cs_tcp_recv.engine
        client_sid = cs_tcp_recv.client_sid
        data = cs_tcp_recv.data
        #
        self.line_finder.accept_bytes(
            barr=data)
    #
    def mi_nearcast_connect(self):
        # xxx fix up configurables
        self.nearcast_orb.nearcast(
            cog_h=self.cog_h,
            message_h='connect',
            username='uname',
            password='pword',
            notes='notes')
    def mi_network_write(self, m):
        if not self.client_sid:
            raise Exception('Not valid to call this with None client sid.')
        self.engine.send(
            sid=self.client_sid,
            data='%s\n'%m)

def cog_console_new(cog_h, nearcast_orb, engine, addr, port):
    ob = CogConsole(
        cog_h=cog_h,
        nearcast_orb=nearcast_orb,
        engine=engine,
        addr=addr,
        port=port)
    return ob


# --------------------------------------------------------
#   :rest
# --------------------------------------------------------
class CogEventSource:
    def __init__(self, cog_h, nearcast_orb, engine):
        self.cog_h = cog_h
        self.nearcast_orb = nearcast_orb
        self.engine = engine
        #
        self.t_something = time.time()
    def at_turn(self):
        "Returns a boolean which is True only if there was activity."
        activity = False
        #
        t_something = time.time()
        if t_something - self.t_something > 1:
            self.nearcast_orb.nearcast(
                cog_h=self.cog_h,
                message_h='something',
                text='here it is!')
            self.t_something = t_something
        #
        return activity

def main():
    init_logging()
    engine = create_engine()
    try:
        nearcast_schema = nearcast_schema_new(
            i_nearcast=I_NEARCAST_SCHEMA)
        nearcast_snoop = nearcast_snoop_new(
            engine=engine,
            nearcast_schema=nearcast_schema,
            addr=TAP_ADDR,
            port=TAP_PORT)
        #
        nearcast_orb = nearcast_orb_new(
            engine=engine,
            nearcast_schema=nearcast_schema,
            nearcast_snoop=nearcast_snoop)
        nearcast_orb.add_cog(
            cog=cog_console_new(
                cog_h='console01',
                nearcast_orb=nearcast_orb,
                engine=engine,
                addr=CONSOLE_ADDR,
                port=CONSOLE_PORT))
        nearcast_orb.add_cog(
            cog=CogEventSource(
                cog_h='esource01',
                nearcast_orb=nearcast_orb,
                engine=engine))
        nearcast_orb.add_cog(
            cog=cog_gruel_client_new(
                cog_h='client01',
                nearcast_orb=nearcast_orb,
                engine=engine,
                addr=TERM_LINK_ADDR,
                port=TERM_LINK_PORT))
        engine.add_orb(
            orb=nearcast_orb)
        engine.event_loop()
    except KeyboardInterrupt:
        pass
    except:
        traceback.print_exc()
    finally:
        engine.close()

if __name__ == '__main__':
    main()

