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
# Simple sandbox for demonstrating that we can communicate with a redis server.

from solent import solent_cpair
from solent import uniq
from solent.eng import engine_new
from solent.exceptions import SolentQuitException
from solent.lc import spin_line_console_new
from solent.log import cformat
from solent.log import init_logging
from solent.log import log
from solent.term import spin_term_new
from solent.redis import rail_resp_etcher_new

from collections import deque
import os
import sys
import time
import traceback

MTU = 1500

CONSOLE_WIDTH = 60
CONSOLE_HEIGHT = 20

I_NEARCAST_SCHEMA = '''
    i message h
        i field h

    message init

    message ex_lc
        field tokens
    message note
        field msg

    message ex_redis
        field msg
    message to_redis
        field msg
    message poke

    message please_open
        field addr
        field port
    message please_close

    message announce_connect
    message announce_condrop
'''

LC_ADDR = 'localhost'
LC_PORT = 6378

REDIS_ADDR = 'localhost'
REDIS_PORT = 6379

class CogLineConsole:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.spin_line_console = engine.init_spin(
            construct=spin_line_console_new,
            cb_lc_connect=lambda cs_lc_connect: None,
            cb_lc_condrop=lambda cs_lc_condrop: None,
            cb_lc_command=self.cb_lc_command)
    #
    def on_init(self):
        self.spin_line_console.start(
            ip=LC_ADDR,
            port=LC_PORT)
    def on_note(self, msg):
        col = cformat(
            string=msg,
            fg='yellow',
            bg='trans')
        self.spin_line_console.send(
            msg='%s\n'%(col))
    #
    def cb_lc_command(self, cs_lc_command):
        tokens = cs_lc_command.tokens
        #
        if 0 == len(tokens):
            return
        self.nearcast.ex_lc(
            tokens=tokens)

class CogInterpreter:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
    #
    def on_ex_lc(self, tokens):
        if 0 == len(tokens):
            return
        #
        first = tokens[0]
        if first == '[': # instruct connect
            self.nearcast.please_open(
                addr=REDIS_ADDR,
                port=REDIS_PORT)
        elif first == ']': # instruct condrop
            self.nearcast.please_close()
        elif first == 'poke':
            self.nearcast.poke()
        elif first == 'say':
            msg = ' '.join(tokens[1:])
            self.nearcast.to_redis(
                msg=msg)
        elif first == 's1':
            msg = '''
                SET users:GeorgeWashington "job: President, born:1732, dislikes: cherry trees"
            '''.strip()
            self.nearcast.to_redis(
                msg=msg)
        elif first == 's2':
            msg = '''
                GET users:GeorgeWashington
            '''.strip()
            self.nearcast.to_redis(
                msg=msg)
        elif first == 's3':
            msg = '''
                DEL users:GeorgeWashington
            '''.strip()
            self.nearcast.to_redis(
                msg=msg)
        else:
            self.nearcast.note(
                msg='!?')
    def on_ex_redis(self, msg):
        self.nearcast.note(
            msg=msg)

class CogRedisClient:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.client_sid = None
        self.rail_resp_etcher = rail_resp_etcher_new(
            mtu=self.engine.mtu,
            cb_etch_head=self.cb_etch_head,
            cb_etch_tail=self.cb_etch_tail,
            cb_etch_pack=self.cb_etch_pack)
        self.rail_resp_parser = rail_resp_parser_new(
            cb_resp_head=self.cb_resp_head,
            cb_resp_tail=self.cb_resp_tail,
            cb_resp_str=self.cb_resp_str,
            cb_resp_err=self.cb_resp_err,
            cb_resp_int=self.cb_resp_int,
            cb_resp_arr_inc=self.cb_resp_arr_inc,
            cb_resp_arr_dec=self.cb_resp_arr_dec)
    #
    def on_please_open(self, addr, port):
        if None != self.client_sid:
            self.nearcast.note(
                msg="already open")
            return
        self.engine.open_tcp_client(
            addr=addr,
            port=port,
            cb_tcp_client_connect=self.cb_tcp_client_connect,
            cb_tcp_client_condrop=self.cb_tcp_client_condrop,
            cb_tcp_client_recv=self.cb_tcp_client_recv)
    def on_please_close(self):
        if None == self.client_sid:
            self.nearcast.note(
                msg='not open')
            return
        self.engine.close_tcp_client(
            client_sid=self.client_sid)
    def on_poke(self):
        if None == self.client_sid:
            return
        self.rail_resp_etcher.open(
            etch_h='unimportant')
        self.rail_resp_etcher.etch_array(2)
        self.rail_resp_etcher.etch_string('LLEN')
        self.rail_resp_etcher.etch_string('mylist')
        self.rail_resp_etcher.close()
    #
    def cb_etch_head(self, cs_etch_head):
        etch_h = cs_etch_head.etch_h
        #
    def cb_etch_tail(self, cs_etch_tail):
        etch_h = cs_etch_tail.etch_h
        #
    def cb_etch_pack(self, cs_etch_pack):
        etch_h = cs_etch_pack.etch_h
        bb = cs_etch_pack.bb
        #
        self.engine.send(
            sid=self.client_sid,
            bb=bb)
    def cb_resp_head(self, cs_resp_head):
        cs_resp_head
        #
    def cb_resp_tail(self, cs_resp_tail):
        cs_resp_tail
        #
    def cb_resp_str(self, cs_resp_str):
        cs_resp_str
        #
    def cb_resp_err(self, cs_resp_err):
        cs_resp_err
        #
    def cb_resp_int(self, cs_resp_int):
        cs_resp_int
        #
    def cb_resp_arr_inc(self, cs_resp_arr_inc):
        cs_resp_arr_inc
        #
    def cb_resp_arr_dec(self, cs_resp_arr_dec):
        cs_resp_arr_dec
        #
    def cb_tcp_client_connect(self, cs_tcp_client_connect):
        engine = cs_tcp_client_connect.engine
        client_sid = cs_tcp_client_connect.client_sid
        addr = cs_tcp_client_connect.addr
        port = cs_tcp_client_connect.port
        #
        self.client_sid = client_sid
        self.nearcast.note(
            msg='opened')
    def cb_tcp_client_condrop(self, cs_tcp_client_condrop):
        engine = cs_tcp_client_condrop.engine
        client_sid = cs_tcp_client_condrop.client_sid
        message = cs_tcp_client_condrop.message
        #
        self.client_sid = None
        self.nearcast.note(
            msg='closed')
    def cb_tcp_client_recv(self, cs_tcp_client_recv):
        engine = cs_tcp_client_recv.engine
        client_sid = cs_tcp_client_recv.client_sid
        bb = cs_tcp_client_recv.bb
        #
        msg = bb.decode('utf8')
        self.nearcast.ex_redis(
            msg=':: %s'%msg)

def main():
    init_logging()
    #
    engine = None
    try:
        engine = engine_new(
            mtu=MTU)
        #
        orb = engine.init_orb(
            i_nearcast=I_NEARCAST_SCHEMA)
        orb.init_cog(CogLineConsole)
        orb.init_cog(CogInterpreter)
        orb.init_cog(CogRedisClient)
        #
        bridge = orb.init_autobridge()
        bridge.nc_init()
        #
        engine.event_loop()
    except KeyboardInterrupt:
        pass
    except SolentQuitException:
        pass
    except:
        traceback.print_exc()
    finally:
        if engine != None:
            engine.close()

if __name__ == '__main__':
    main()

