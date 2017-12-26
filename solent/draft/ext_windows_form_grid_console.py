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
from solent import log
from solent import solent_ext
from solent import SolentQuitException
from solent.util import RailLineConsole

import cProfile


# --------------------------------------------------------
#   model
# --------------------------------------------------------
I_NEARCAST = '''
    i message h
    i field h

    message prime
        field lc_addr
        field lc_port
    message init
    message splat
        field zero_h
        field msg
'''

class TrackPrime:
    def __init__(self, orb):
        self.orb = orb
    def on_prime(self, lc_addr, lc_port):
        self.lc_addr = lc_addr
        self.lc_port = lc_port

class CogToLineConsole:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.track_prime = orb.track(TrackPrime)
        #
        self.rail_line_console = RailLineConsole()
    def on_init(self):
        rail_h = '%s/line_console'%(self.cog_h)
        self.rail_line_console.zero(
            rail_h=rail_h,
            cb_line_console_connect=self.cb_line_console_connect,
            cb_line_console_condrop=self.cb_line_console_condrop,
            cb_line_console_command=self.cb_line_console_command,
            engine=self.engine)
        #
        ip = self.track_prime.lc_addr
        port = self.track_prime.lc_port
        self.rail_line_console.start(
            ip=ip,
            port=port)
    def cb_line_console_connect(self, cs_line_console_connect):
        rail_h = cs_line_console_connect.rail_h
        #
        pass
    def cb_line_console_condrop(self, cs_line_console_condrop):
        rail_h = cs_line_console_condrop.rail_h
        #
        pass
    def cb_line_console_command(self, cs_line_console_command):
        rail_h = cs_line_console_command.rail_h
        tokens = cs_line_console_command.tokens
        #
        cmd = tokens[0]
        rest = tokens[1:]
        if cmd == 'q':
            raise SolentQuitException()
        else:
            self.rail_line_console.send('  ??\r\n')

class CogToGridConsole:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
    def on_init(self):
        zero_h = 'main/form_grid_console'
        form_grid_console = solent_ext(
            ext='windows_form_grid_console',
            zero_h=zero_h,
            cb_grid_console_splat=self.cb_grid_console_splat,
            cb_grid_console_resize=self.cb_grid_console_resize,
            cb_grid_console_kevent=self.cb_grid_console_kevent,
            cb_grid_console_mevent=self.cb_grid_console_mevent,
            cb_grid_console_closed=self.cb_grid_console_closed,
            engine=self.engine,
            width=800,
            height=600)
        #
        # xxx
        form_grid_console.close()
    def cb_grid_console_splat(self, cs_grid_console_splat):
        zero_h = cs_grid_console_splat.zero
        #
        pass
    def cb_grid_console_resize(self, cs_grid_console_resize):
        zero_h = cs_grid_console_resize.zero_h
        #
        xxx
    def cb_grid_console_kevent(self, cs_grid_console_kevent):
        zero_h = cs_grid_console_kevent.zero_h
        keycode = cs_grid_console_kevent.keycode
        #
        log('received keycode |%s|'%(keycode))
    def cb_grid_console_mevent(self, cs_grid_console_mevent):
        zero_h = cs_grid_console_mevent.zero_h
        #
        xxx
    def cb_grid_console_closed(self, cs_grid_console_closed):
        zero_h = cs_grid_console_closed.zero_h
        #
        xxx

class CogBridge:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
    def on_splat(self, zero_h, msg):
        log('[%s] %s'%(zero_h, msg))
        raise SolentQuitException()

def init_nearcast(engine, lc_addr, lc_port):
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST)
    orb.add_log_snoop()
    #
    orb.init_cog(CogToGridConsole)
    orb.init_cog(CogToLineConsole)
    #
    bridge = orb.init_cog(CogBridge)
    bridge.nearcast.prime(
        lc_addr=lc_addr,
        lc_port=lc_port)
    bridge.nearcast.init()
    return bridge


# --------------------------------------------------------
#   bootstrap
# --------------------------------------------------------
MTU = 1490

LC_ADDR = '127.0.0.1'
LC_PORT = 7788

def main():
    engine = Engine(
        mtu=MTU)
    #
    try:
        init_nearcast(
            engine=engine,
            lc_addr=LC_ADDR,
            lc_port=LC_PORT)
        engine.event_loop()
    except KeyboardInterrupt:
        pass
    except SolentQuitException:
        pass
    finally:
        engine.close()
        log("after engine close")

if __name__ == '__main__':
    #cProfile.run('main()')
    main()

