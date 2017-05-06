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

from solent.log import log

from collections import deque

class CsRedisClientOpened:
    def __init__(self):
        pass

class CsRedisClientClosed:
    def __init__(self):
        pass

class CsRedisClientData:
    def __init__(self):
        self.bb = None

class CsRedisClientFail:
    def __init__(self):
        self.msg = None

CONSTATE_DORMANT = 'dormant'
CONSTATE_ATTEMPT = 'attempt'
CONSTATE_IS_OPEN = 'is_open'

class SpinRedisClient:
    def __init__(self, spin_h, engine, cb_redis_client_opened, cb_redis_client_closed, cb_redis_client_data, cb_redis_client_fail):
        self.spin_h = spin_h
        self.engine = engine
        self.cb_redis_client_opened = cb_redis_client_opened
        self.cb_redis_client_closed = cb_redis_client_closed
        self.cb_redis_client_data = cb_redis_client_data
        self.cb_redis_client_fail = cb_redis_client_fail
        #
        self.cs_redis_client_opened = CsRedisClientOpened()
        self.cs_redis_client_closed = CsRedisClientClosed()
        self.cs_redis_client_data = CsRedisClientData()
        self.cs_redis_client_fail = CsRedisClientFail()
        #
        self.constate = CONSTATE_DORMANT
        self.client_sid = None
        self.send_buffer = deque()
    def eng_turn(self, activity):
        if self.constate == CONSTATE_IS_OPEN and self.send_buffer:
            activity.mark(
                l=self,
                s='sending towards redis')
            bb = self.send_buffer.popleft()
            self.engine.send(
                sid=self.client_sid,
                bb=bb)
    def eng_close(self):
        pass
    #
    def is_open(self):
        return self.constate == CONSTATE_IS_OPEN
    def open(self, ip, port):
        if self.constate == CONSTATE_ATTEMPT:
            self._call_redis_client_fail(
                msg="still attempting earlier open request")
            return
        if self.constate == CONSTATE_IS_OPEN:
            self._call_redis_client_fail(
                msg="already open")
            return
        #
        self.constate = CONSTATE_ATTEMPT
        self.client_sid = self.engine.open_tcp_client(
            addr=ip,
            port=port,
            cb_tcp_client_connect=self.cb_tcp_client_connect,
            cb_tcp_client_condrop=self.cb_tcp_client_condrop,
            cb_tcp_client_recv=self.cb_tcp_client_recv)
    def close(self):
        if self.constate == CONSTATE_DORMANT:
            self._call_redis_client_fail(
                msg="not open to be closed")
            return
        #
        self.engine.close_tcp_client(
            client_sid=self.client_sid)
    def send(self, msg):
        if not self.constate == CONSTATE_IS_OPEN:
            self._call_redis_client_fail(
                msg="line is not open")
            return
        #
        bb = bytes("%s\r\n"%(msg), 'utf8')
        mtu = self.engine.mtu
        while len(bb) > mtu:
            self.send_buffer.append(bb[:mtu])
            bb = bb[mtu:]
        self.send_buffer.append(bb)
    #
    def _call_redis_client_opened(self):
        self.cb_redis_client_opened(
            cs_redis_client_opened=self.cs_redis_client_opened)
    def _call_redis_client_closed(self):
        self.cb_redis_client_closed(
            cs_redis_client_closed=self.cs_redis_client_closed)
    def _call_redis_client_data(self, bb):
        self.cs_redis_client_data.bb = bb
        self.cb_redis_client_data(
            cs_redis_client_data=self.cs_redis_client_data)
    def _call_redis_client_fail(self, msg):
        self.cs_redis_client_fail.msg = msg
        self.cb_redis_client_fail(
            cs_redis_client_fail=self.cs_redis_client_fail)
    #
    def cb_tcp_client_connect(self, cs_tcp_client_connect):
        engine = cs_tcp_client_connect.engine
        client_sid = cs_tcp_client_connect.client_sid
        addr = cs_tcp_client_connect.addr
        port = cs_tcp_client_connect.port
        #
        log('cb_tcp_client_connect')
        self.constate = CONSTATE_IS_OPEN
        #
        self._call_redis_client_opened()
    def cb_tcp_client_condrop(self, cs_tcp_client_condrop):
        engine = cs_tcp_client_condrop.engine
        client_sid = cs_tcp_client_condrop.client_sid
        message = cs_tcp_client_condrop.message
        #
        log('cb_tcp_client_condrop')
        self.client_sid = None
        self.constate = CONSTATE_DORMANT
        #
        self._call_redis_client_closed()
    def cb_tcp_client_recv(self, cs_tcp_client_recv):
        engine = cs_tcp_client_recv.engine
        client_sid = cs_tcp_client_recv.client_sid
        bb = cs_tcp_client_recv.bb
        #
        self._call_redis_client_data(
            bb=bb)

def spin_redis_client_new(spin_h, engine, cb_redis_client_opened, cb_redis_client_closed, cb_redis_client_data, cb_redis_client_fail):
    ob = SpinRedisClient(
        spin_h=spin_h,
        engine=engine,
        cb_redis_client_opened=cb_redis_client_opened,
        cb_redis_client_closed=cb_redis_client_closed,
        cb_redis_client_data=cb_redis_client_data,
        cb_redis_client_fail=cb_redis_client_fail)
    return ob

