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

from solent import uniq
from solent import Engine
from solent import log
from solent import run_tests
from solent import test
from solent.util import RailLineConsole

import sys

MTU = 1500

class Receiver:
    def __init__(self):
        self.sb = []
        self.b_connected = False
    def on_line_console_connect(self, cs_line_console_connect):
        rail_h = cs_line_console_connect.rail_h
        addr = cs_line_console_connect.addr
        port = cs_line_console_connect.port
        #
        self.b_connected = True
    def on_line_console_condrop(self, cs_line_console_condrop):
        rail_h = cs_line_console_condrop.rail_h
        msg = cs_line_console_condrop.msg
        #
        self.b_connected = False
    def on_line_console_command(self, cs_line_console_command):
        rail_h = cs_line_console_command.rail_h
        tokens = cs_line_console_command.tokens
        #
        self.sb.append(tokens)

class SpinBasicTcpClient:
    def __init__(self, spin_h, engine):
        self.spin_h = spin_h
        self.engine = engine
        #
        self.client_sid = None
        self.sb = None
    def eng_turn(self, activity):
        pass
    def eng_close(self):
        if self.client_sid != None:
            self.engine.close_tcp_client(
                client_sid=self.client_sid)
    #
    def is_connected(self):
        return self.client_sid != None
    def start(self, addr, port):
        self.engine.open_tcp_client(
            addr=addr,
            port=port,
            cb_tcp_client_connect=self.cb_tcp_client_connect,
            cb_tcp_client_condrop=self.cb_tcp_client_condrop,
            cb_tcp_client_recv=self.cb_tcp_client_recv)
    def send(self, msg):
        bb = bytes(msg, 'utf8')
        self.engine.send(
            sid=self.client_sid,
            bb=bb)
    def stop(self):
        self.engine.close_tcp_client(
            client_sid=self.client_sid)
    #
    def cb_tcp_client_connect(self, cs_tcp_client_connect):
        engine = cs_tcp_client_connect.engine
        client_sid = cs_tcp_client_connect.client_sid
        addr = cs_tcp_client_connect.addr
        port = cs_tcp_client_connect.port
        #
        self.client_sid = client_sid
        self.sb = []
    def cb_tcp_client_condrop(self, cs_tcp_client_condrop):
        engine = cs_tcp_client_condrop.engine
        client_sid = cs_tcp_client_condrop.client_sid
        message = cs_tcp_client_condrop.message
        #
        self.client_sid = None
        self.sb = None
    def cb_tcp_client_recv(self, cs_tcp_client_recv):
        engine = cs_tcp_client_recv.engine
        client_sid = cs_tcp_client_recv.client_sid
        bb = cs_tcp_client_recv.bb
        #
        msg = bb.decode('utf8')
        self.sb.append(msg)

@test
def should_start_and_stop_without_crashing():
    receiver = Receiver()
    #
    engine = Engine(
        mtu=MTU)
    rail_line_console = RailLineConsole()
    rail_h = 'test/line_console'
    rail_line_console.zero(
        rail_h=rail_h,
        cb_line_console_connect=receiver.on_line_console_connect,
        cb_line_console_condrop=receiver.on_line_console_condrop,
        cb_line_console_command=receiver.on_line_console_command,
        engine=engine)
    engine.cycle()
    #
    # Stage: Start it
    rail_line_console.start(
        ip='localhost',
        port=5000)
    #
    # Verify
    engine.cycle()
    assert rail_line_console.is_server_listening() == True
    assert rail_line_console.is_accept_connected() == False
    #
    # Stage: Stop it
    rail_line_console.stop()
    #
    # Verify
    engine.cycle()
    assert rail_line_console.is_server_listening() == False
    assert rail_line_console.is_accept_connected() == False
    #
    return True

@test
def should_accept_client_and_boot_client_on_stop():
    ip = 'localhost'
    port = 5000
    #
    engine = Engine(
        mtu=MTU)
    receiver = Receiver()
    #
    # step: start
    rail_line_console = RailLineConsole()
    rail_h = 'test/line_console'
    rail_line_console.zero(
        rail_h=rail_h,
        cb_line_console_connect=receiver.on_line_console_connect,
        cb_line_console_condrop=receiver.on_line_console_condrop,
        cb_line_console_command=receiver.on_line_console_command,
        engine=engine)
    rail_line_console.start(
        ip=ip,
        port=port)
    #
    # verify
    engine.cycle()
    assert rail_line_console.is_server_listening() == True
    assert rail_line_console.is_accept_connected() == False
    #
    # step: client connects
    client = engine.init_spin(
        construct=SpinBasicTcpClient)
    client.start(
        addr=ip,
        port=port)
    #
    # verify
    engine.cycle()
    assert rail_line_console.is_server_listening() == False
    assert rail_line_console.is_accept_connected() == True
    assert client.is_connected() == True
    #
    # step: server is stopped with client attached
    rail_line_console.stop()
    #
    # confirm effects
    engine.cycle()
    assert rail_line_console.is_server_listening() == False
    assert rail_line_console.is_accept_connected() == False
    assert client.is_connected() == False
    #
    return True

@test
def should_transfer_of_text():
    ip = 'localhost'
    port = 5000
    #
    engine = Engine(
        mtu=MTU)
    receiver = Receiver()
    #
    # step: start it
    rail_line_console = RailLineConsole()
    rail_h = 'test/line_console'
    rail_line_console.zero(
        rail_h=rail_h,
        cb_line_console_connect=receiver.on_line_console_connect,
        cb_line_console_condrop=receiver.on_line_console_condrop,
        cb_line_console_command=receiver.on_line_console_command,
        engine=engine)
    rail_line_console.start(
        ip=ip,
        port=port)
    #
    # verify
    engine.cycle()
    assert rail_line_console.is_server_listening() == True
    assert rail_line_console.is_accept_connected() == False
    #
    # step: client connects
    client = engine.init_spin(
        construct=SpinBasicTcpClient)
    client.start(
        addr=ip,
        port=port)
    #
    # verify
    engine.cycle()
    assert rail_line_console.is_server_listening() == False
    assert rail_line_console.is_accept_connected() == True
    assert client.is_connected() == True
    #
    # step: client sends text that does not have a newline
    client.send(
        msg="abc def") # emphasis: no newline
    #
    # verify: we should not have received a line
    engine.cycle()
    assert 0 == len(receiver.sb)
    #
    # step: now send a new line and some overflow
    client.send(
        msg="\noverflow")
    client.send(
        msg="/second half")
    #
    # verify: we should have seen our first line
    engine.cycle()
    assert 1 == len(receiver.sb)
    assert receiver.sb[0] == ['abc', 'def']
    #
    # step: another line ending
    client.send(
        msg='\n')
    #
    # verify
    engine.cycle()
    assert 2 == len(receiver.sb)
    assert receiver.sb[-1] == ['overflow/second', 'half']
    #
    # step: multiple lines in one pass
    client.send(
        msg="three\nfour\n")
    #
    # verify
    engine.cycle()
    assert 4 == len(receiver.sb)
    assert receiver.sb[-2] == ['three',]
    assert receiver.sb[-1] == ['four',]
    #
    # step: we write to client
    s = "here is some text\n"
    rail_line_console.send(
        msg=s)
    #
    # verify
    engine.cycle()
    assert 1 == len(client.sb)
    assert client.sb[-1] == s
    #
    return True

if __name__ == '__main__':
    run_tests()

