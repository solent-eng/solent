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
# [This is incomplete at time if writing]
#
# Here is a more complex application of the principles from some of the TCP
# scenarios (e.g. 20, 21).
#
# Here we use the line console to send commands over the nearcast. We run the
# command console itself. Then, there are cogs offering functionality on other
# sockets. There other cogs are not the focus of this scenario, but are a
# preview of functionality that will be offered later in these scenarios.
#
# To use this command console:
# * Run the application
# * Netcat to its port (see CONSOLE_PORT below)
# * Type '?'
#
# // exercise
# Copy the code below to your own directory. Set up a venv and install
# solent to it.
#
# Then:
#   *   How could you modify this so that a user who connects to the
#       application console needs to enter a password?

from solent import Engine
from solent import SolentQuitException
from solent import log
from solent.util import RailLineFinder

import traceback


# --------------------------------------------------------
#   command shell
# --------------------------------------------------------
class CsShellError:
    def __init__(self):
        self.msg = None

class CsShellInfo:
    def __init__(self):
        self.msg = None

class CsShellDisconnect:
    def __init__(self):
        self.msg = None

class CsShellPubStart:
    def __init__(self):
        self.pub_h = None
        self.port = None
        self.duration = None
        self.word = None

class CsShellPubStop:
    def __init__(self):
        self.pub_h = None

class CsShellPubSend:
    def __init__(self):
        self.pub_h = None
        self.msg = None

class CsShellSubStart:
    def __init__(self):
        self.sub_h = None
        self.port = None
        self.duration = None

class CsShellSubStop:
    def __init__(self):
        self.sub_h = None

class RailCommandShell:
    def __init__(self):
        self.cs_shell_error = CsShellError()
        self.cs_shell_info = CsShellInfo()
        self.cs_shell_disconnect = CsShellDisconnect()
        self.cs_shell_pub_start = CsShellPubStart()
        self.cs_shell_pub_stop = CsShellPubStop()
        self.cs_shell_pub_send = CsShellPubSend()
        self.cs_shell_sub_start = CsShellSubStart()
        self.cs_shell_sub_stop = CsShellSubStop()
    def zero(self, cb_shell_error, cb_shell_info, cb_shell_disconnect, cb_shell_pub_start, cb_shell_pub_stop, cb_shell_pub_send, cb_shell_sub_start, cb_shell_sub_stop):
        self.cb_shell_error = cb_shell_error
        self.cb_shell_info = cb_shell_info
        self.cb_shell_disconnect = cb_shell_disconnect
        self.cb_shell_pub_start = cb_shell_pub_start
        self.cb_shell_pub_stop = cb_shell_pub_stop
        self.cb_shell_pub_send = cb_shell_pub_send
        self.cb_shell_sub_start = cb_shell_sub_start
        self.cb_shell_sub_stop = cb_shell_sub_stop
    #
    def accept(self, line):
        cmd_functions = ['_'.join(fn_name.split('_')[1:])
            for fn_name in dir(self)
            if fn_name.startswith('cmd_')]
        tokens = [t
            for t in line.split(' ')
            if len(t) > 0]
        (cmd, rest) = (tokens[0], tokens[1:])
        if cmd == '?':
            names = sorted(cmd_functions)
            self._call_shell_info(
                msg='\n'.join(names))
        elif cmd not in cmd_functions:
            self._call_shell_error(
                msg="No command %s. (Try ?)"%(cmd))
        else:
            fn = getattr(self, 'cmd_%s'%(cmd))
            fn(rest)
    #
    def cmd_quit(self, tokens):
        self._call_shell_disconnect(
            msg='')
    def cmd_test(self, tokens):
        self._call_shell_info(
            msg='wohoo!')
    def cmd_pub_start(self, tokens):
        log('%s'%str(tokens))
        try:
            (pub_h, port, duration, word) = tokens
            port = int(port)
            duration = int(duration)
        except:
            traceback.print_exc()
            self._call_shell_error(
                msg='usage:')
            self._call_shell_error(
                msg='  pub_start pub_h port duration word')
            return
        self._call_shell_pub_start(
            pub_h=pub_h,
            port=port,
            duration=duration,
            word=word)
    #
    def _call_shell_error(self, msg):
        self.cs_shell_error.msg = msg
        self.cb_shell_error(
            cs_shell_error=self.cs_shell_error)
    def _call_shell_info(self, msg):
        self.cs_shell_info.msg = msg
        self.cb_shell_info(
            cs_shell_info=self.cs_shell_info)
    def _call_shell_disconnect(self, msg):
        self.cs_shell_disconnect.msg = msg
        self.cb_shell_disconnect(
            cs_shell_disconnect=self.cs_shell_disconnect)
    def _call_shell_pub_start(self, pub_h, port, duration, word):
        self.cs_shell_pub_start.pub_h = pub_h
        self.cs_shell_pub_start.port = port
        self.cs_shell_pub_start.duration = duration
        self.cs_shell_pub_start.word = word
        self.cb_shell_pub_start(
            cs_shell_pub_start=self.cs_shell_pub_start)
    def _call_shell_pub_stop(self, pub_h):
        self.cs_shell_pub_stop.pub_h = pub_h
        self.cb_shell_pub_stop(
            cs_shell_pub_stop=self.cs_shell_pub_stop)
    def _call_shell_pub_send(self, pub_h, msg):
        self.cs_shell_pub_send.pub_h = pub_h
        self.cs_shell_pub_send.msg = msg
        self.cb_shell_pub_send(
            cs_shell_pub_send=self.cs_shell_pub_send)
    def _call_shell_sub_start(self, sub_h, port, duration):
        self.cs_shell_sub_start.sub_h = sub_h
        self.cs_shell_sub_start.port = port
        self.cs_shell_sub_start.duration = duration
        self.cb_shell_sub_start(
            cs_shell_sub_start=self.cs_shell_sub_start)
    def _call_shell_sub_stop(self, sub_h):
        self.cs_shell_sub_stop.sub_h = sub_h
        self.cb_shell_sub_stop(
            cs_shell_sub_stop=self.cs_shell_sub_stop)


# --------------------------------------------------------
#   model
# --------------------------------------------------------
I_NEARCAST = '''
    i message h
        i field h

    message init
        field console_addr
        field console_port
    message error
        field msg
    message exit

    message start_udp_pub
        field pub_h
        field port
        field duration
        field word
    message stop_udp_pub
        field pub_h

    message start_udp_sub
        field port
    message stop_udp_sub

    message user_line
        field msg
'''

class CogAppConsole:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.b_active = False
        self.console_addr = None
        self.console_port = None
        self.server_sid = None
        self.accept_sid = None
        #
        self.rail_line_finder = RailLineFinder()
        self.rail_line_finder.zero(
            cb_found_line=self.cb_found_line)
        self.rail_command_shell = RailCommandShell()
    def orb_close(self):
        if self.server_sid:
            self._stop_server()
        if self.accept_sid:
            self.engine.close_tcp_server(
                server_sid=self.server_sid)
    #
    def on_init(self, console_addr, console_port):
        self.console_addr = console_addr
        self.console_port = console_port
        #
        self.b_active = True
        self._start_server()
    def on_error(self, msg):
        if self.accept_sid:
            self.engine.send(
                sid=self.accept_sid,
                msg=msg)
    def on_exit(self):
        self.b_active = False
        self._stop_server()
    #
    def cb_shell_error(self, cs_shell_error):
        msg = cs_shell_error.msg
        #
        msg_out = 'ERROR: %s\n'%(msg)
        bb = bytes(msg_out, 'utf8')
        self.engine.send(
            sid=self.accept_sid,
            bb=bb)
    def cb_shell_info(self, cs_shell_info):
        msg = cs_shell_info.msg
        #
        msg_out = '%s\n'%(msg)
        bb = bytes(msg_out, 'utf8')
        self.engine.send(
            sid=self.accept_sid,
            bb=bb)
    def cb_shell_disconnect(self, cs_shell_disconnect):
        msg = cs_shell_disconnect.msg
        #
        self._boot_client()
    def cb_shell_pub_start(self, cs_shell_pub_start):
        pub_h = cs_shell_pub_start.pub_h
        port = cs_shell_pub_start.port
        duration = cs_shell_pub_start.duration
        word = cs_shell_pub_start.word
        #
        self.nearcast.start_udp_pub(
            pub_h=pub_h,
            port=port,
            duration=duration,
            word=word)
    def cb_shell_pub_stop(self, cs_shell_put_stop):
        pub_h = cs_shell_pub_stop.pub_h
        #
        log('xxx')
    def cb_shell_pub_send(self, cs_shell_pub_send):
        pub_h = cs_shell_pub_send.pub_h
        msg = cs_shell_pub_send.msg
        #
        log('xxx')
    def cb_shell_sub_start(self, cs_shell_sub_start):
        sub_h = cs_shell_sub_start.sub_h
        port = cs_shell_sub_start.port
        duration = cs_shell_sub_start.duration
        #
        log('xxx')
    def cb_shell_sub_stop(self, cs_shell_sub_stop):
        sub_h = cs_shell_sub_stop.sub_h
        #
        log('xxx')
    #
    def cb_found_line(self, cs_found_line):
        msg = cs_found_line.msg
        #
        self.rail_command_shell.accept(
            line=msg)
    #
    def cb_tcp_server_start(self, cs_tcp_server_start):
        engine = cs_tcp_server_start.engine
        server_sid = cs_tcp_server_start.server_sid
        addr = cs_tcp_server_start.addr
        port = cs_tcp_server_start.port
        #
        self.server_sid = server_sid
        log('cb_tcp_server_start, sid %s, at %s:%s'%(server_sid, addr, port))
    def cb_tcp_server_stop(self, cs_tcp_server_stop):
        engine = cs_tcp_server_stop.engine
        server_sid = cs_tcp_server_stop.server_sid
        msg = cs_tcp_server_stop.message
        #
        self.server_sid = None
        log('cb_tcp_server_stop, sid %s, %s'%(server_sid, msg))
    def cb_tcp_accept_connect(self, cs_tcp_accept_connect):
        engine = cs_tcp_accept_connect.engine
        server_sid = cs_tcp_accept_connect.server_sid
        accept_sid = cs_tcp_accept_connect.accept_sid
        accept_addr = cs_tcp_accept_connect.accept_addr
        accept_port = cs_tcp_accept_connect.accept_port
        #
        log('cb_tcp_accept_connect from %s:%s'%(
            accept_addr, accept_port))
        self.engine.close_tcp_server(
            server_sid=self.server_sid)
        self.accept_sid = accept_sid
        self.rail_line_finder.clear()
        self.rail_command_shell.zero(
            cb_shell_error=self.cb_shell_error,
            cb_shell_info=self.cb_shell_info,
            cb_shell_disconnect=self.cb_shell_disconnect,
            cb_shell_pub_start=self.cb_shell_pub_start,
            cb_shell_pub_stop=self.cb_shell_pub_stop,
            cb_shell_pub_send=self.cb_shell_pub_send,
            cb_shell_sub_start=self.cb_shell_sub_start,
            cb_shell_sub_stop=self.cb_shell_sub_stop)
    def cb_tcp_accept_condrop(self, cs_tcp_accept_condrop):
        engine = cs_tcp_accept_condrop.engine
        server_sid = cs_tcp_accept_condrop.server_sid
        accept_sid = cs_tcp_accept_condrop.accept_sid
        #
        log('cb_tcp_accept_condrop from %s'%(
            accept_sid))
        self.accept_sid = None
        if self.b_active:
            self._start_server()
    def cb_tcp_accept_recv(self, cs_tcp_accept_recv):
        engine = cs_tcp_accept_recv.engine
        accept_sid = cs_tcp_accept_recv.accept_sid
        bb = cs_tcp_accept_recv.bb
        #
        msg = bb.decode('utf8')
        self.rail_line_finder.accept_string(
            s=msg)
    #
    def _start_server(self):
        self.engine.open_tcp_server(
            addr=self.console_addr,
            port=self.console_port,
            cb_tcp_server_start=self.cb_tcp_server_start,
            cb_tcp_server_stop=self.cb_tcp_server_stop,
            cb_tcp_accept_connect=self.cb_tcp_accept_connect,
            cb_tcp_accept_condrop=self.cb_tcp_accept_condrop,
            cb_tcp_accept_recv=self.cb_tcp_accept_recv)
    def _stop_server(self):
        self.engine.close_tcp_server(
            server_sid=self.server_sid)
    def _boot_client(self):
        self.engine.close_tcp_accept(
            accept_sid=self.accept_sid)

class CogPubManager:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
    def on_start_udp_pub(self, pub_h, port, duration, word):
        # xxx buffer this information, and complete the pub setup.
        # /note that we will need a map of pubs, not just a single.
        self.open_pub(
            addr='127.0.0.1',
            port=port,
            cb_pub_start=self.cb_pub_start,
            cb_pub_stop=self.cb_pub_stop)
    def on_stop_udp_pub(self, pub_h):
        xxx

class CogSubManager:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine

def contain_event_loop(engine):
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST)
    orb.init_cog(CogAppConsole)
    orb.init_cog(CogPubManager)
    orb.init_cog(CogSubManager)
    orb.add_log_snoop()
    #
    bridge = orb.init_autobridge()
    bridge.nc_init(
        console_addr=CONSOLE_ADDR,
        console_port=CONSOLE_PORT)
    #
    engine.event_loop()


# --------------------------------------------------------
#   launch
# --------------------------------------------------------
MTU = 1400

CONSOLE_ADDR = '0.0.0.0'
CONSOLE_PORT = 8000

def main():
    engine = Engine(
        mtu=MTU)
    try:
        contain_event_loop(
            engine=engine)
    except KeyboardInterrupt:
        pass
    except SolentQuitException:
        pass
    finally:
        engine.close()

if __name__ == '__main__':
    main()

