#
# engine (testing)
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

from solent.util import uniq

from testing.util import clock_fake

class Engine:
    def __init__(self):
        #
        self.clock = clock_fake()
        self.events = []
        self.sent_data = []
        #
        self.mtu = 500
    def get_clock(self):
        return self.clock
    def send(self, sid, data):
        self.sent_data.append(data[:])
    def open_tcp_client(self, addr, port, cb_tcp_connect, cb_tcp_condrop, cb_tcp_recv):
        self.events.append( ('open_tcp_client', addr, port) )
        return 'fake_sid_%s'%uniq()
    def open_tcp_server(self, addr, port, cb_tcp_connect, cb_tcp_condrop, cb_tcp_recv):
        self.events.append( ('open_tcp_server', addr, port) )
        return 'fake_sid_%s'%uniq()
    def close_tcp_server(self, sid):
        self.events.append( ('close_tcp_server',) )
    def close_tcp_client(self, sid):
        self.events.append( ('close_tcp_client',) )

def engine_fake():
    ob = Engine()
    return ob

