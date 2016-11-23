#!/usr/bin/env python3
#
# Sandbox
#
# // brief
# This is being used for developing new functionality.
#
# // deprecated
# This will disappear in time. Don't use it as a dependency.
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
from solent.eng import nearcast_orb_new
from solent.eng import nearcast_schema_new
from solent.eng import nearcast_snoop_new
from solent.log import init_logging
from solent.log import log

from collections import deque
import traceback


# --------------------------------------------------------
#   :cog_gruel_server
# --------------------------------------------------------
#
# xxx this will all need to get refactored. I have been trying to do too many
# things in this cog class. But I'm developing the new approach on the client
# side. Will revisit that once I understand the ideas.
#
class CogGruelServer(object):
    def __init__(self, name, engine, addr, port):
        self.name = name
        self.engine = engine
        self.addr = addr
        self.port = port
        # form: (addr, port) : deque containing data
        self.received = {}
        self.server_sid = engine.open_tcp_server(
            addr=addr,
            port=port,
            cb_tcp_connect=self.engine_on_tcp_connect,
            cb_tcp_condrop=self.engine_on_tcp_condrop,
            cb_tcp_recv=self.engine_on_tcp_recv)
    def close(self):
        self.engine.close_tcp_server(self.server_sid)
    def engine_on_tcp_connect(self, cs_tcp_connect):
        engine = cs_tcp_connect.engine
        client_sid = cs_tcp_connect.client_sid
        addr = cs_tcp_connect.addr
        port = cs_tcp_connect.port
        #
        log("connect/%s/%s/%s/%s"%(
            self.name,
            client_sid,
            addr,
            port))
        key = (engine, client_sid)
        self.received[key] = deque()
        engine.send(
            sid=client_sid,
            data='')
    def engine_on_tcp_condrop(self, cs_tcp_condrop):
        engine = cs_tcp_condrop.engine
        client_sid = cs_tcp_condrop.client_sid
        message = cs_tcp_condrop.message
        #
        log("condrop/%s/%s/%s"%(self.name, client_sid, message))
        key = (engine, client_sid)
        del self.received[key]
    def engine_on_tcp_recv(self, cs_tcp_recv):
        engine = cs_tcp_recv.engine
        client_sid = cs_tcp_recv.client_sid
        data = cs_tcp_recv.data
        #
        print('recv! %s'%data) # xxx
        key = (engine, client_sid)
        self.received[key].append(data)
        engine.send(
            sid=client_sid,
            data='received %s\n'%len(data))
    def at_turn(self, activity):
        pass

def cog_gruel_server_new(name, engine, addr, port):
    ob = CogGruelServer(
        name=name,
        engine=engine,
        addr=addr,
        port=port)
    return ob


# --------------------------------------------------------
#   :rest
# --------------------------------------------------------
# xxx
TERM_LINK_ADDR = '127.0.0.1'
TERM_LINK_PORT = 4100

I_NEARCAST_SCHEMA = '''
    i message h
    i field h
    
    message send_something
        field text
'''

def create_orb(engine):
    orb = nearcast_orb_new(
        engine=engine,
        nearcast_schema=nearcast_schema_new(
            i_nearcast=I_NEARCAST_SCHEMA))
    orb.add_cog(
        cog=cog_gruel_server_new(
            name='server01',
            engine=engine,
            addr=TERM_LINK_ADDR,
            port=TERM_LINK_PORT))
    return orb

def main():
    init_logging()
    engine = engine_new()
    try:
        engine.add_orb(
            orb=create_orb(
                engine=engine))
        engine.event_loop()
    except KeyboardInterrupt:
        pass
    except:
        traceback.print_exc()
    finally:
        engine.close()

if __name__ == '__main__':
    main()

