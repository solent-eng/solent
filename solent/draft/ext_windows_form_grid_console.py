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

from solent import e_keycode
from solent import Engine
from solent import log
from solent import solent_cpair
from solent import solent_ext
from solent import SolentQuitException
from solent.console import Cgrid
from solent.util import RailLineConsole

import cProfile


# --------------------------------------------------------
#   enum
# --------------------------------------------------------
MTYPE_PLAYER = 'player'
MTYPE_AI = 'ai'


# --------------------------------------------------------
#   model
# --------------------------------------------------------
I_NEARCAST = '''
    i message h
    i field h

    message prime
        field lc_addr
        field lc_port
        field console_width
        field console_height
    message init
    message splat
        field zero_h
        field msg

    message render

    message grid_kevent
        field keycode

    message mob_o
        field mob_h
    message mob_set
        field mob_h
        field mtype
        field drop
        field rest
        field c
        field cpair
    message mob_x
        field mob_h
'''

class TrackPrime:
    def __init__(self, orb):
        self.orb = orb
    def on_prime(self, lc_addr, lc_port, console_width, console_height):
        self.lc_addr = lc_addr
        self.lc_port = lc_port
        self.console_width = console_width
        self.console_height = console_height

class ShapeMob:
    def __init__(self):
        self.mob_h = None
        self.mtype = None
        self.drop = None
        self.rest = None
        self.c = None
        self.cpair = None
        self.pos = None

class TrackMob:
    def __init__(self, orb):
        self.orb = orb
        #
        self.player = None
        # mobs are tracked here
        self.d = {}
        # (drop, rest) vs [list of shape_mob]
        self.pos = {}
    def on_mob_o(self, mob_h):
        shape_mob = ShapeMob()
        shape_mob.mob_h = None
        shape_mob.mtype = None
        shape_mob.drop = None
        shape_mob.rest = None
        shape_mob.c = None
        shape_mob.cpair = None
        shape_mob.pos = None
        self.d[mob_h] = shape_mob
    def on_mob_set(self, mob_h, mtype, drop, rest, c, cpair):
        shape_mob = self.d[mob_h]
        shape_mob.mob_h = mob_h
        shape_mob.mtype = mtype
        shape_mob.drop = drop
        shape_mob.rest = rest
        shape_mob.c = c
        shape_mob.cpair = cpair
        #
        pos_key = (drop, rest)
        if pos_key not in self.pos:
            self.pos[pos_key] = []
        #
        if shape_mob.pos != None:
            self.pos[shape_mob.pos].remove(shape_mob)
        self.pos[pos_key].append(shape_mob)
        shape_mob.pos = pos_key
        #
        if mtype == MTYPE_PLAYER:
            self.player = shape_mob
    def on_mob_x(self, mob_h):
        mob = self.d[mob_h]
        drop = mob.drop
        rest = mob.rest
        del mob
        del self.d[mob_h]
        #
        pos_key = (drop, rest)
        self.pos[pos_key].remove(mob)
    def top_mobs(self):
        for ((drop, rest), lst_mob) in self.pos.items():
            if not lst_mob:
                continue
            mob = lst_mob[-1]
            yield (drop, rest, mob)
    def get_pos(self, drop, rest):
        pos_key = (mob.drop, mob.rest)
        if pos_key not in self.pos:
            self.pos[pos_key] = []
        return self.pos[pos_key]

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
        #
        self.track_prime = orb.track(TrackPrime)
        self.track_mob = orb.track(TrackMob)
        #
        self.form_grid_console = None
        self.cgrid = None
    def on_init(self):
        self.cgrid = Cgrid(
            width=self.track_prime.console_width,
            height=self.track_prime.console_height)
        #
        zero_h = '%s/form_grid_console'%(self.cog_h)
        self.form_grid_console = solent_ext(
            ext='solent.ext.windows_form_grid_console',
            zero_h=zero_h,
            cb_grid_console_splat=self.cb_grid_console_splat,
            cb_grid_console_kevent=self.cb_grid_console_kevent,
            cb_grid_console_mevent=self.cb_grid_console_mevent,
            cb_grid_console_closed=self.cb_grid_console_closed,
            engine=self.engine,
            width=self.track_prime.console_width,
            height=self.track_prime.console_height)
    def on_render(self):
        self.cgrid.clear()
        for (drop, rest, mob) in self.track_mob.top_mobs():
            s = mob.c
            cpair = mob.cpair
            self.cgrid.put( 
                drop=drop,
                rest=rest,
                s=s,
                cpair=cpair)
        self.form_grid_console.send(self.cgrid)
    #
    def cb_grid_console_splat(self, cs_grid_console_splat):
        zero_h = cs_grid_console_splat.zero
        msg = cs_grid_console_splat.msg
        #
        self.nearcast.splat(
            zero_h=zero_h,
            msg=msg)
    def cb_grid_console_kevent(self, cs_grid_console_kevent):
        zero_h = cs_grid_console_kevent.zero_h
        keycode = cs_grid_console_kevent.keycode
        #
        self.nearcast.grid_kevent(
            keycode=keycode)
    def cb_grid_console_mevent(self, cs_grid_console_mevent):
        zero_h = cs_grid_console_mevent.zero_h
        #
        xxx
    def cb_grid_console_closed(self, cs_grid_console_closed):
        zero_h = cs_grid_console_closed.zero_h
        #
        xxx

class CogToGame:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.track_prime = orb.track(TrackPrime)
        self.track_mob = orb.track(TrackMob)
    def on_init(self):
        self._setup_mobs()
        self.nearcast.render()
    def on_grid_kevent(self, keycode):
        log('received keycode |%s| {%s}'%(keycode, e_keycode(keycode)))
        #
        if keycode == e_keycode.Q:
            raise SolentQuitException()
        elif keycode == e_keycode.h:
            shape_mob = self.track_mob.player
            mob_h = shape_mob.mob_h
            mtype = shape_mob.mtype
            drop = shape_mob.drop
            rest = shape_mob.rest - 1
            c = shape_mob.c
            cpair = shape_mob.cpair
            self.nearcast.mob_set(
                mob_h=mob_h,
                mtype=mtype,
                drop=drop,
                rest=rest,
                c=c,
                cpair=cpair)
        elif keycode == e_keycode.j:
            shape_mob = self.track_mob.player
            mob_h = shape_mob.mob_h
            mtype = shape_mob.mtype
            drop = shape_mob.drop + 1
            rest = shape_mob.rest
            c = shape_mob.c
            cpair = shape_mob.cpair
            self.nearcast.mob_set(
                mob_h=mob_h,
                mtype=mtype,
                drop=drop,
                rest=rest,
                c=c,
                cpair=cpair)
        elif keycode == e_keycode.k:
            shape_mob = self.track_mob.player
            mob_h = shape_mob.mob_h
            mtype = shape_mob.mtype
            drop = shape_mob.drop - 1
            rest = shape_mob.rest
            c = shape_mob.c
            cpair = shape_mob.cpair
            self.nearcast.mob_set(
                mob_h=mob_h,
                mtype=mtype,
                drop=drop,
                rest=rest,
                c=c,
                cpair=cpair)
        elif keycode == e_keycode.l:
            shape_mob = self.track_mob.player
            mob_h = shape_mob.mob_h
            mtype = shape_mob.mtype
            drop = shape_mob.drop
            rest = shape_mob.rest + 1
            c = shape_mob.c
            cpair = shape_mob.cpair
            self.nearcast.mob_set(
                mob_h=mob_h,
                mtype=mtype,
                drop=drop,
                rest=rest,
                c=c,
                cpair=cpair)
        #
        self.nearcast.render()
    def _setup_mobs(self):
        self.nearcast.mob_o(
            mob_h=0)
        cpair = solent_cpair('green')
        self.nearcast.mob_set(
            mob_h=0,
            mtype=MTYPE_PLAYER,
            drop=4,
            rest=4,
            c='@',
            cpair=cpair)
        #
        self.nearcast.mob_o(
            mob_h=1)
        cpair = solent_cpair('red')
        self.nearcast.mob_set(
            mob_h=1,
            mtype=MTYPE_AI,
            drop=3,
            rest=8,
            c='h',
            cpair=cpair)

class CogBridge:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
    def on_splat(self, zero_h, msg):
        log('[%s] %s'%(zero_h, msg))
        raise SolentQuitException()

def init_nearcast(engine, lc_addr, lc_port, console_width, console_height):
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST)
    orb.add_log_snoop()
    #
    orb.init_cog(CogToGridConsole)
    orb.init_cog(CogToLineConsole)
    orb.init_cog(CogToGame)
    #
    bridge = orb.init_cog(CogBridge)
    bridge.nearcast.prime(
        lc_addr=lc_addr,
        lc_port=lc_port,
        console_width=console_width,
        console_height=console_height)
    bridge.nearcast.init()
    return bridge


# --------------------------------------------------------
#   bootstrap
# --------------------------------------------------------
MTU = 1490

LC_ADDR = '127.0.0.1'
LC_PORT = 7788

CONSOLE_WIDTH = 30
CONSOLE_HEIGHT = 14

def main():
    engine = Engine(
        mtu=MTU)
    engine.set_default_timeout(0.08)
    #
    try:
        init_nearcast(
            engine=engine,
            lc_addr=LC_ADDR,
            lc_port=LC_PORT,
            console_width=CONSOLE_WIDTH,
            console_height=CONSOLE_HEIGHT)
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

