#
# spin_line_console (testing)
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

from testing import run_tests
from testing import test
from testing.eng import engine_fake
from testing.util import clock_fake

from solent.eng import activity_new
from solent.eng import cs
from solent.eng import orb_new
from solent.lc import lc_nearcast_schema_new
from solent.lc import spin_line_console_new
from solent.log import log
from solent.log import hexdump_bytearray
from solent.util import uniq

import sys

class LineAcc:
    def __init__(self):
        self.lines = []
    def on_line(self, line):
        self.lines.append(line)

def simulate_client_connect(engine, server_sid, ip, port):
    engine.simulate_tcp_client_connect(
        server_sid=server_sid,
        client_ip=ip,
        client_port=port)

@test
def should_start_with_no_services_active():
    engine = engine_fake()
    line_acc = LineAcc()
    spin_line_console = spin_line_console_new(
        engine=engine,
        cb_line=line_acc.on_line)
    #
    # confirm baseline
    assert None == spin_line_console.server_sid
    assert None == spin_line_console.client_sid
    #
    return True

@test
def should_start_and_stop_server():
    engine = engine_fake()
    line_acc = LineAcc()
    spin_line_console = spin_line_console_new(
        engine=engine,
        cb_line=line_acc.on_line)
    #
    spin_line_console.start(
        ip='127.0.0.1',
        port=4080)
    assert None != spin_line_console.server_sid
    assert None == spin_line_console.client_sid
    #
    spin_line_console.stop()
    assert None == spin_line_console.server_sid
    assert None == spin_line_console.client_sid
    #
    return True

@test
def should_accept_client_and_boot_client_on_stop():
    engine = engine_fake()
    line_acc = LineAcc()
    spin_line_console = spin_line_console_new(
        engine=engine,
        cb_line=line_acc.on_line)
    #
    spin_line_console.start(
        ip='127.0.0.1',
        port=4080)
    #
    # scenario: client connects
    client_ip = '203.15.93.2'
    client_port = 1234
    simulate_client_connect(
        engine=engine,
        server_sid=spin_line_console.server_sid,
        ip=client_ip,
        port=client_port)
    #
    # confirm effects
    assert None == spin_line_console.server_sid
    assert None != spin_line_console.client_sid
    #
    # scenario: server is stopped with client attached
    spin_line_console.stop()
    #
    # confirm effects
    assert None == spin_line_console.server_sid
    assert None == spin_line_console.client_sid
    #
    return True

@test
def should_transfer_of_text():
    engine = engine_fake()
    line_acc = LineAcc()
    spin_line_console = spin_line_console_new(
        engine=engine,
        cb_line=line_acc.on_line)
    # server start
    spin_line_console.start(
        ip='127.0.0.1',
        port=4080)
    # client connects
    client_sid = 'fake_sid_%s'%(uniq())
    cs_tcp_connect = cs.CsTcpConnect()
    cs_tcp_connect.engine = engine
    cs_tcp_connect.client_sid = client_sid
    cs_tcp_connect.addr = '203.15.93.2'
    cs_tcp_connect.port = 1234
    spin_line_console._engine_on_tcp_connect(
        cs_tcp_connect=cs_tcp_connect)
    #
    def send_data(text):
        utf8_bytes = bytes(text, 'utf8')
        cs_tcp_recv = cs.CsTcpRecv()
        cs_tcp_recv.engine = engine
        cs_tcp_recv.client_sid = client_sid
        cs_tcp_recv.data = utf8_bytes
        spin_line_console._engine_on_tcp_recv(
            cs_tcp_recv=cs_tcp_recv)
    #
    # scenario: client sends text that does not have a newline
    send_data(
        text="abc") # emphasis: no newline
    # should not have received a line
    assert 0 == len(line_acc.lines)
    #
    # scenario: now we get a newline and some overflow
    send_data(
        text="\noverflow")
    assert 1 == len(line_acc.lines)
    assert line_acc.lines[-1] == 'abc'
    #
    # scenario: another line
    send_data(
        text="/second half\n")
    assert 2 == len(line_acc.lines)
    assert line_acc.lines[-1] == 'overflow/second half'
    #
    # scenario: multiple lines in one pass
    send_data(
        text="three\nfour\n")
    assert 4 == len(line_acc.lines)
    assert line_acc.lines[-2] == 'three'
    assert line_acc.lines[-1] == 'four'
    #
    # scenario: we write to client
    s = "here is some text"
    spin_line_console.write_to_client(
        s=s)
    assert 1 == len(engine.sent_data)
    assert engine.sent_data[-1] == s
    #
    return True

if __name__ == '__main__':
    run_tests(
        unders_file=sys.modules['__main__'].__file__)

