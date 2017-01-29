#!/usr/bin/python -B
#
# tclient
#
# // overview
# Simple tcp client tool. You could think of it as being similar to netcat.
# The motive for writing it is that I do not have something to hand on
# Windows, and I'm working through the engine scenarios for that platform.
# For the moment I'm just hard-coding it to pygame. If you're in unix,
# you probably have something else handy.
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

from solent import solent_cpair
from solent import solent_keycode
from solent.eng import engine_new
from solent.log import init_logging
from solent.log import log
from solent.log import hexdump_bytes
from solent.term import spin_term_new
from solent.util import line_finder_new

import sys
import time
import traceback

I_NEARCAST_SCHEMA = '''
    i message h
        i field h

    message init
        field addr
        field port

    message tcp_connect
    message tcp_condrop
        field message

    message netrecv
        field bb

    message netsend
        field bb
'''

CONSOLE_TYPE = 'pygame'
CONSOLE_WIDTH = 78
CONSOLE_HEIGHT = 24

class CogTcpClient:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.sid_tcp_client = None
    def at_close(self):
        self.engine.close_tcp_client(
            sid=self.sid_broadcast_sender)
    def at_turn(self, activity):
        if self.sid_tcp_client == None:
            return
    def on_init(self, addr, port):
        self.sid_tcp_client = self.engine.open_tcp_client(
            addr=addr,
            port=port,
            cb_tcp_connect=self.engine_on_tcp_connect,
            cb_tcp_condrop=self.engine_on_tcp_condrop,
            cb_tcp_recv=self.engine_on_tcp_recv)
    def on_netsend(self, bb):
        self.engine.send(
            sid=self.sid_tcp_client,
            payload=bb)
    #
    def engine_on_tcp_connect(self, cs_tcp_connect):
        engine = cs_tcp_connect.engine
        client_sid = cs_tcp_connect.client_sid
        addr = cs_tcp_connect.addr
        port = cs_tcp_connect.port
        #
        self.nearcast.tcp_connect()
    def engine_on_tcp_condrop(self, cs_tcp_condrop):
        engine = cs_tcp_condrop.engine
        client_sid = cs_tcp_condrop.client_sid
        message = cs_tcp_condrop.message
        #
        self.nearcast.tcp_condrop(
            message=message)
    def engine_on_tcp_recv(self, cs_tcp_recv):
        engine = cs_tcp_recv.engine
        client_sid = cs_tcp_recv.client_sid
        data = cs_tcp_recv.data
        #
        self.nearcast.netrecv(
            bb=data)

class CogTerm:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.spin_term = None
        self.line_finder = None
        self.drop = None
        self.rest = None
    def at_close(self):
        pass
    def at_turn(self, activity):
        if None != self.spin_term:
            self.spin_term.at_turn(
                activity=activity)
    def on_init(self, addr, port):
        self.spin_term = spin_term_new(
            console_type=CONSOLE_TYPE,
            cb_keycode=self.term_on_keycode,
            cb_select=self.term_on_select)
        self.spin_term.open_console(
            width=CONSOLE_WIDTH,
            height=CONSOLE_HEIGHT)
        self.drop = 0
        self.rest = 0
        self.spin_term.refresh_console()
    def on_tcp_connect(self):
        self.line_finder = line_finder_new(
            cb_line=self.lfinder_on_line)
        #
        self.spin_term.clear()
        self.spin_term.write(
            drop=0,
            rest=0,
            s='Connected',
            cpair=solent_cpair('red'))
        self.drop = 1
        self.rest = 0
        self.spin_term.refresh_console()
    def on_tcp_condrop(self, message):
        self.line_finder = None
        #
        self.spin_term.clear()
        self.spin_term.write(
            drop=0,
            rest=0,
            s=message,
            cpair=solent_cpair('red'))
        self.drop = 1
        self.rest = 0
        self.spin_term.refresh_console()
    def on_netrecv(self, bb):
        for keycode in bb:
            self._print(
                keycode=keycode,
                cpair=solent_cpair('grey'))
        self.spin_term.refresh_console()
    #
    def term_on_keycode(self, keycode):
        if None == self.line_finder:
            return
        #
        cpair = solent_cpair('orange')
        # This backspace mechanism is far from perfect.
        if keycode == solent_keycode('backspace'):
            self.line_finder.backspace()
            s = self.line_finder.get()
            idx = len(s)%CONSOLE_WIDTH
            s = s[-1*idx:]
            self.spin_term.write(
                drop=self.drop,
                rest=0,
                s='%s '%s,
                cpair=cpair)
            self.rest = len(s)
        else:
            self.line_finder.accept_bytes([keycode])
            self._print(
                keycode=keycode,
                cpair=cpair)
        self.spin_term.refresh_console()
    def term_on_select(self, drop, rest):
        pass
    def lfinder_on_line(self, line):
        self.nearcast.netsend(
            bb=bytes('%s\n'%line, 'utf8'))
    #
    def _print(self, keycode, cpair):
        if keycode == solent_keycode('backspace') and self.rest > 0:
            self.rest -= 1
            self.spin_term.write(
                drop=self.drop,
                rest=self.rest,
                s=' ',
                cpair=cpair)
            return
        if keycode == solent_keycode('newline'):
            self.rest = 0
            self.drop += 1
        else:
            self.spin_term.write(
                drop=self.drop,
                rest=self.rest,
                s=chr(keycode),
                cpair=cpair)
            self.rest += 1
        if self.rest == CONSOLE_WIDTH:
            self.rest = 0
            self.drop += 1
        while self.drop >= CONSOLE_HEIGHT:
            self.spin_term.scroll()
            self.drop -= 1

class CogBridge:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
    def nc_init(self, addr, port):
        self.nearcast.init(
            addr=addr,
            port=port)

def usage():
    print('Usage:')
    print('  %s addr port'%sys.argv[0])
    sys.exit(1)

def main():
    if 3 != len(sys.argv):
        usage()
    #
    init_logging()
    engine = engine_new(
        mtu=1492)
    try:
        net_addr = sys.argv[1]
        net_port = int(sys.argv[2])
        #
        orb = engine.init_orb(
            orb_h=__name__,
            i_nearcast=I_NEARCAST_SCHEMA)
        orb.add_log_snoop()
        orb.init_cog(CogTcpClient)
        orb.init_cog(CogTerm)
        bridge = orb.init_cog(CogBridge)
        bridge.nc_init(
            addr=net_addr,
            port=net_port)
        #
        engine.event_loop()
    except KeyboardInterrupt:
        pass
    except:
        traceback.print_exc()
    finally:
        engine.close()

if __name__ == '__main__':
    main()



