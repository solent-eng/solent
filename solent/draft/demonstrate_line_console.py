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

from solent import Engine
from solent import SolentQuitException
from solent import log
from solent.util import RailLineConsole

LC_ADDR = 'localhost'
LC_PORT = 8200

MTU = 1490

I_NEARCAST = '''
    i message h
    i field h

    message init

    message line_console_connect
        field addr
        field port
    message line_console_condrop
        field msg
    message to_line_console
        field s

    message cmd_add
        field a
        field b
    message cmd_echo
        field s
    message cmd_quit
'''

class CogInterpret:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
    def on_cmd_add(self, a, b):
        a = int(a)
        b = int(b)
        log("%s + %s = %s"%(a, b, a+b))
    def on_cmd_echo(self, s):
        self.nearcast.to_line_console(
            s=s)
    def on_cmd_quit(self):
        raise SolentQuitException()

class CogToLineConsole:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.rail_line_console = RailLineConsole()
    #
    def on_init(self):
        rail_h='%s/line_console'%(self.cog_h)
        self.rail_line_console.zero(
            rail_h=rail_h,
            cb_line_console_connect=self.cb_line_console_connect,
            cb_line_console_condrop=self.cb_line_console_condrop,
            cb_line_console_command=self.cb_line_console_command,
            engine=self.engine)
        #
        self.rail_line_console.start(
            ip=LC_ADDR,
            port=LC_PORT)
    def on_to_line_console(self, s):
        self.rail_line_console.send(
            msg='%s\n'%s)
    #
    def cb_line_console_connect(self, cs_line_console_connect):
        addr = cs_line_console_connect.addr
        port = cs_line_console_connect.port
        #
        self.nearcast.line_console_connect(
            addr=addr,
            port=port)
    def cb_line_console_condrop(self, cs_line_console_condrop):
        msg = cs_line_console_condrop.msg
        #
        self.nearcast.line_console_condrop(
            msg=msg)
    def cb_line_console_command(self, cs_line_console_command):
        tokens = cs_line_console_command.tokens
        #
        def complain(msg):
            self.rail_line_console.send(
                msg='%s\n'%msg)
        #
        if 0 == len(tokens):
            pass
        elif tokens[0] == 'add':
            if 3 != len(tokens):
                complain('Usage: add a b')
                return
            (_, a, b) = tokens
            self.nearcast.cmd_add(
                a=a,
                b=b)
        elif tokens[0] == 'echo':
            if 2 != len(tokens):
                complain('Usage: echo s')
                return
            (_, s) = tokens
            self.nearcast.cmd_echo(
                s=s)
        elif tokens[0] == 'quit':
            self.nearcast.cmd_quit()
        else:
            complain('??')
            return

class CogBridge:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
    def nc_init(self):
        self.nearcast.init()

def main():
    engine = Engine(
        mtu=MTU)
    try:
        orb = engine.init_orb(
            i_nearcast=I_NEARCAST)
        orb.add_log_snoop()
        orb.init_cog(CogInterpret)
        orb.init_cog(CogToLineConsole)
        bridge = orb.init_cog(CogBridge)
        bridge.nc_init()
        engine.event_loop()
    except SolentQuitException:
        pass
    except KeyboardInterrupt:
        pass
    finally:
        engine.close()

if __name__ == '__main__':
    main()

