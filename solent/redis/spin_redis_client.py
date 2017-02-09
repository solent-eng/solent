#
# spin_redis_client
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

from solent.log import log

class SpinRedisClient:
    def __init__(self, spin_h, engine, cb_ex_redis):
        self.spin_h = spin_h
        self.engine = engine
        self.cb_ex_redis = cb_ex_redis
        #
        self.client_sid = None
    def at_turn(self, activity):
        pass
    def at_close(self):
        pass
    #
    def start(self, ip, port):
        self.engine.open_tcp_client(
            addr=ip,
            port=port,
            cb_tcp_client_connect=self._engine_on_tcp_client_connect,
            cb_tcp_client_condrop=self._engine_on_tcp_client_condrop,
            cb_tcp_client_recv=self._engine_on_tcp_client_recv)
    def stop(self):
        self.engine.close_tcp_client(
            client_sid=self.client_sid)
    def send(self, msg):
        bb = bytes("%s\r\n"%(msg), 'utf8')
        self.engine.send(
            sid=self.client_sid,
            bb=bb)
    #
    def _engine_on_tcp_client_connect(self, cs_tcp_client_connect):
        engine = cs_tcp_client_connect.engine
        client_sid = cs_tcp_client_connect.client_sid
        addr = cs_tcp_client_connect.addr
        port = cs_tcp_client_connect.port
        #
        log('_engine_on_tcp_client_connect')
        self.client_sid = client_sid
    def _engine_on_tcp_client_condrop(self, cs_tcp_client_condrop):
        engine = cs_tcp_client_condrop.engine
        client_sid = cs_tcp_client_condrop.client_sid
        message = cs_tcp_client_condrop.message
        #
        log('_engine_on_tcp_client_condrop')
        self.client_sid = None
    def _engine_on_tcp_client_recv(self, cs_tcp_client_recv):
        engine = cs_tcp_client_recv.engine
        client_sid = cs_tcp_client_recv.client_sid
        bb = cs_tcp_client_recv.bb
        #
        msg = bb.decode('utf8')
        self.cb_ex_redis(
            msg=msg)

def spin_redis_client_new(spin_h, engine, cb_ex_redis):
    ob = SpinRedisClient(
        spin_h=spin_h,
        engine=engine,
        cb_ex_redis=cb_ex_redis)
    return ob

