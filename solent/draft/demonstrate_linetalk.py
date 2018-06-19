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
from solent.util import RailLinetalk

LC_ADDR = 'localhost'
LC_PORT = 8200

MTU = 1490

I_NEARCAST = '''
    i message h
    i field h

    message init

    message linetalk_connect
        field accept_sid
        field addr
        field port
    message linetalk_condrop
        field accept_sid
        field msg

    message cmd_add
        field accept_sid
        field a
        field b
    message cmd_echo
        field accept_sid
        field s
    message cmd_quit
        field accept_sid

    message result
        field accept_sid
        field msg
'''

class CogInterpret:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
    def on_cmd_add(self, accept_sid, a, b):
        a = int(a)
        b = int(b)

        msg = "%s + %s = %s"%(a, b, a+b)
        self.nearcast.result(
            accept_sid=accept_sid,
            msg=msg)
    def on_cmd_echo(self, accept_sid, s):
        msg = s
        self.nearcast.result(
            accept_sid=accept_sid,
            msg=msg)
    def on_cmd_quit(self, accept_sid):
        raise SolentQuitException()

class CogToLinetalk:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.rail_linetalk = RailLinetalk()
    #
    def on_init(self):
        zero_h = '%s/linetalk'%(self.cog_h)
        self.rail_linetalk.zero(
            zero_h=zero_h,
            cb_linetalk_connect=self.cb_linetalk_connect,
            cb_linetalk_condrop=self.cb_linetalk_condrop,
            cb_linetalk_command=self.cb_linetalk_command,
            engine=self.engine)
        self.rail_linetalk.set_login('uu', 'pp')
        #
        self.rail_linetalk.start(
            ip=LC_ADDR,
            port=LC_PORT)
    def on_result(self, accept_sid, msg):
        self.rail_linetalk.send(
            accept_sid=accept_sid,
            msg='%s\n'%msg)
    #
    def cb_linetalk_connect(self, cs_linetalk_connect):
        accept_sid = cs_linetalk_connect.accept_sid
        addr = cs_linetalk_connect.addr
        port = cs_linetalk_connect.port
        #
        self.nearcast.linetalk_connect(
            accept_sid=accept_sid,
            addr=addr,
            port=port)
    def cb_linetalk_condrop(self, cs_linetalk_condrop):
        accept_sid = cs_linetalk_condrop.accept_sid
        msg = cs_linetalk_condrop.msg
        #
        self.nearcast.linetalk_condrop(
            accept_sid=accept_sid,
            msg=msg)
    def cb_linetalk_command(self, cs_linetalk_command):
        accept_sid = cs_linetalk_command.accept_sid
        tokens = cs_linetalk_command.tokens
        #
        def complain(msg):
            self.rail_linetalk.send(
                accept_sid=accept_sid,
                msg='%s\n'%msg)
        #
        log('tokens |%s|'%(str(tokens)))
        if 0 == len(tokens):
            pass
        elif tokens[0] == 'add':
            if 3 != len(tokens):
                complain('Usage: add a b')
                return
            (_, a, b) = tokens
            self.nearcast.cmd_add(
                accept_sid=accept_sid,
                a=a,
                b=b)
        elif tokens[0] == 'echo':
            if 2 != len(tokens):
                complain('Usage: echo s')
                return
            (_, s) = tokens
            self.nearcast.cmd_echo(
                accept_sid=accept_sid,
                s=s)
        elif tokens[0] == 'quit':
            self.nearcast.cmd_quit(
                accept_sid=accept_sid)
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
        orb.init_cog(CogToLinetalk)
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

