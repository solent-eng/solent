#!/usr/bin/env python3
#
# Gruel server sandbox
#
# // brief
# Demonstrates an application that incorporated a gruel server.
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

from solent.eng import engine_new
from solent.eng import nearcast_schema_new
from solent.eng import log_snoop_new
from solent.eng import orb_new
from solent.gruel import spin_gruel_server_new
from solent.lc import spin_line_console_new
from solent.log import cformat
from solent.log import init_logging
from solent.log import log

from collections import deque
import traceback

SERVER_ADDR = '127.0.0.1'
SERVER_PORT = 4100
SERVER_PASS = 'qweasd'

SNOOP_ADDR = '127.0.0.1'
SNOOP_PORT = 4090

LC_ADDR = '127.0.0.1'
LC_PORT = 4091

I_NEARCAST_SCHEMA = '''
    i message h
    i field h

    message lc_input
        field line
    
    message lc_output
        field s

    message start_gruel_server
        field addr
        field port
        field password

    message stop_gruel_server

    message doc_recv
        field doc

    message doc_send
        field doc
'''

class CogLcServer(object):
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.spin_line_console = spin_line_console_new(
            engine=engine,
            cb_line=self.lc_on_line)
        self.spin_line_console.start(
            ip=LC_ADDR,
            port=LC_PORT)
    #
    def lc_on_line(self, line):
        self.orb.nearcast(
            cog_h=self.cog_h,
            message_h='lc_input',
            line=line)
    #
    def on_lc_output(self, s):
        col = cformat(
            string=s,
            fg='yellow',
            bg='trans')
        log(col)
        self.spin_line_console.write_to_client(
            s='%s\n'%(col))

class CogInterpretLineConsole(object):
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.commands = {
            'start': self.cmd_start,
            'stop': self.cmd_stop,
            '?': self.cmd_help,
            'help': self.cmd_help}
    #
    def on_lc_input(self, line):
        # This is really primitive not even going to parse it. :)
        line = line.strip()
        if line not in self.commands:
            self.orb.nearcast(
                cog_h=self.cog_h,
                message_h='lc_output',
                s='syntax error')
            return
        cmd = self.commands[line]
        cmd()
    #
    def cmd_start(self):
        self.orb.nearcast(
            cog_h=self.cog_h,
            message_h='start_gruel_server',
            addr=SERVER_ADDR,
            port=SERVER_PORT,
            password=SERVER_PASS)
    def cmd_stop(self):
        self.orb.nearcast(
            cog_h=self.cog_h,
            message_h='stop_gruel_server')
    def cmd_help(self):
        self.orb.nearcast(
            cog_h=self.cog_h,
            message_h='lc_output',
            s='\n'.join(sorted(self.commands.keys())))

class CogGruelServer(object):
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.spin_gruel_server = spin_gruel_server_new(
            engine=engine,
            cb_doc_recv=self._gruel_on_doc)
    def at_turn(self, activity):
        self.spin_gruel_server.at_turn(
            activity=activity)
    def on_start_gruel_server(self, addr, port, password):
        self.spin_gruel_server.start(
            addr=addr,
            port=port,
            password=password)
    def _gruel_on_doc(self, doc):
        self.orb.nearcast(
            cog_h=self.cog_h,
            message_h='doc_recv',
            doc=doc)

def main():
    init_logging()
    engine = engine_new(
        mtu=1500)
    try:
        nearcast_schema = nearcast_schema_new(
            i_nearcast=I_NEARCAST_SCHEMA)
        snoop = log_snoop_new(
            nearcast_schema=nearcast_schema)
        orb = engine.init_orb(
            nearcast_schema=nearcast_schema,
            snoop=snoop)
        #
        orb.init_cog(CogLcServer)
        orb.init_cog(CogInterpretLineConsole)
        orb.init_cog(CogGruelServer)
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

