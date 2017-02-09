#!/usr/bin/env python3
#
# redis client
#
# // overview
# Simple sandbox for demonstrating that we can communicate with a redis server.
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
from solent import uniq
from solent.eng import engine_new
from solent.exceptions import SolentQuitException
from solent.lc import spin_line_console_new
from solent.log import cformat
from solent.log import init_logging
from solent.log import log
from solent.redis import spin_redis_client_new
from solent.term import spin_term_new

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

    message ex_lc
        field msg
    message to_lc
        field msg

    message ex_redis
        field msg
    message to_redis
        field msg

    message please_connect
        field addr
        field port
    message please_condrop

    message announce_connect
    message announce_condrop
'''

LC_ADDR = 'localhost'
LC_PORT = 6378

REDIS_ADDR = 'localhost'
REDIS_PORT = 6379

class CogLc:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.spin_line_console = engine.init_spin(
            construct=spin_line_console_new)
        self.spin_line_console.start(
            ip=LC_ADDR,
            port=LC_PORT,
            cb_connect=lambda: None,
            cb_condrop=lambda: None,
            cb_line=self._lc_on_line)
    #
    def on_to_lc(self, msg):
        col = cformat(
            string=msg,
            fg='yellow',
            bg='trans')
        self.spin_line_console.send(
            msg='%s\n'%(col))
    #
    def _lc_on_line(self, line):
        self.nearcast.ex_lc(
            msg=line)

class CogInterpreter:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
    def on_ex_lc(self, msg):
        tokens = [l for l in msg.split(' ') if len(l) > 0]
        if '' == msg:
            return
        elif msg == 'connect':
            self.nearcast.please_connect(
                addr=REDIS_ADDR,
                port=REDIS_PORT)
            self.nearcast.to_lc(
                msg='ok')
        elif tokens[0] == 'say':
            msg = ' '.join(tokens[1:])
            self.nearcast.to_redis(
                msg=msg)
        elif msg == 'condrop':
            self.nearcast.please_condrop()
            self.nearcast.to_lc(
                msg='ok')
        else:
            self.nearcast.to_lc(
                msg='!?')
    def on_ex_redis(self, msg):
        self.nearcast.to_lc(
            msg=msg)

class CogRedisClient:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.spin_redis_client = engine.init_spin(
            construct=spin_redis_client_new,
            cb_ex_redis=self._redis_ex_redis)
    def on_please_connect(self, addr, port):
        self.spin_redis_client.start(
            ip=addr,
            port=port)
    def on_please_condrop(self):
        self.spin_redis_client.stop()
    def on_to_redis(self, msg):
        self.spin_redis_client.send(
            msg=msg)
    def _redis_ex_redis(self, msg):
        self.nearcast.ex_redis(
            msg=msg)

def main():
    init_logging()
    #
    engine = None
    try:
        engine = engine_new(
            mtu=MTU)
        engine.default_timeout = 0.04
        #
        orb = engine.init_orb(
            spin_h='app',
            i_nearcast=I_NEARCAST_SCHEMA)
        orb.init_cog(CogLc)
        orb.init_cog(CogInterpreter)
        orb.init_cog(CogRedisClient)
        engine.event_loop()
    except SolentQuitException:
        pass
    except:
        traceback.print_exc()
    finally:
        if engine != None:
            engine.close()

if __name__ == '__main__':
    main()

