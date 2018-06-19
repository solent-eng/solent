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
# Quick demo of how you would build a multi-user dungeon.

from solent import Engine
from solent import log
from solent import SolentQuitException
from solent.util import RailLinetalk


# --------------------------------------------------------
#   game model
# --------------------------------------------------------
class Session:

    def __init__(self, user):
        self.name = user
        self.inv = []


# --------------------------------------------------------
#   event model
# --------------------------------------------------------
I_NEARCAST = '''
    i message h
        i field h

    message prime_linetalk
        field addr
        field port
    message init

    message intent_look
    message action_look
        field list_stuff

    message intent_get
        field thing
    message action_get_done
    message action_get_fail
        
'''

class TrackPrime:

    def __init__(self, orb):
        self.orb = orb

    def on_prime_linetalk(self, addr, port):
        self.linetalk_addr = addr
        self.linetalk_port = port


class CogLinetalk:

    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine

        self.track_prime = self.orb.track(TrackPrime)

        self.rail_linetalk = RailLinetalk()
        self.auth = {
            'jane': 'pass',
            'drew': 'pass'}

        self.d_session = {}

    def on_init(self):
        zero_h = '%s/linetalk'%(self.cog_h)
        self.rail_linetalk.zero(
            zero_h=zero_h,
            cb_linetalk_connect=self.cb_linetalk_connect,
            cb_linetalk_conauth=self.cb_linetalk_conauth,
            cb_linetalk_condrop=self.cb_linetalk_condrop,
            cb_linetalk_command=self.cb_linetalk_command,
            engine=self.engine)
        for (uu, pp) in self.auth.items():
            self.rail_linetalk.set_login(uu, pp)

        self.rail_linetalk.start(
            ip=self.track_prime.linetalk_addr,
            port=self.track_prime.linetalk_port)

    def cb_linetalk_connect(self, cs_linetalk_connect):
        accept_sid = cs_linetalk_connect.accept_sid
        addr = cs_linetalk_connect.addr
        port = cs_linetalk_connect.port

        pass

    def cb_linetalk_conauth(self, cs_linetalk_conauth):
        accept_sid = cs_linetalk_conauth.accept_sid
        addr = cs_linetalk_conauth.addr
        port = cs_linetalk_conauth.port
        user = cs_linetalk_conauth.user

        self.d_session[accept_sid] = Session(
            user=user)

    def cb_linetalk_condrop(self, cs_linetalk_condrop):
        accept_sid = cs_linetalk_condrop.accept_sid
        msg = cs_linetalk_condrop.msg

        del self.d_session[accept_sid]

    def cb_linetalk_command(self, cs_linetalk_command):
        accept_sid = cs_linetalk_command.accept_sid
        tokens = cs_linetalk_command.tokens

        session = self.d_session[accept_sid]

        log('linetalk command |%s|'%(tokens))

def init_nearcast(engine, linetalk_addr, linetalk_port):
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST)
    orb.init_cog(CogLinetalk)
    #
    bridge = orb.init_autobridge()
    bridge.nearcast.prime_linetalk(
        addr=linetalk_addr,
        port=linetalk_port)
    bridge.nearcast.init()


# --------------------------------------------------------
#   launch
# --------------------------------------------------------
MTU = 1400

LINETALK_ADDR = '0.0.0.0'
LINETALK_PORT = 8000

def main():
    engine = Engine(
        mtu=MTU)
    try:
        init_nearcast(
            engine=engine,
            linetalk_addr=LINETALK_ADDR,
            linetalk_port=LINETALK_PORT)
        engine.event_loop()
    except KeyboardInterrupt:
        pass
    except SolentQuitException:
        pass
    finally:
        engine.close()

if __name__ == '__main__':
    main()


