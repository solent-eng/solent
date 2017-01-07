#
# swamp monster
#
# // overview
# Adaptation of a previous 7d-roguelike to solent. Being designed within
# CogRoguebox (solent.draft.roguebox).
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

from .chart import chart_new
from .swamp import swamp_new

from solent import e_colpair
from solent.eng import nearcast_schema_new
from solent.log import log
from solent.util import uniq

import random

I_NEARCAST = '''
    i message h
        i field h

    message init
        field height
        field width

    message box_display
        field message

    message full_refresh

    message sigil
        field h

    message tile
        field sigil_h
        field drop
        field rest

    message meep
        field h
        field rest
        field drop
        field c
        field cpair

    message input_nw
    message input_nn
    message input_ne
    message input_sw
    message input_ss
    message input_se
    message input_ww
    message input_ee
    message input_bump

    message move_player
        field h
        field drop
        field rest

    message move_monster
        field h
        field drop
        field rest

    message end_of_round

    message display_clear
    message display_put
        field drop
        field rest
        field s
        field cpair
'''

DM_NAV = uniq()
DM_BOX = uniq()

class PinDisplayMode:
    def __init__(self):
        self.mode = None
    #
    def on_init(self, height, width):
        self.mode = DM_NAV
    #
    def is_nav_mode(self):
        return self.mode == DM_NAV
    def is_box_mode(self):
        return self.mode == DM_BOX

SIGIL_VOID = ' '
SIGIL_WATER = '~'
SIGIL_LAND = '.'
SIGIL_MANGROVE = '%'
SIGIL_MONSTER = 'Y'
SIGIL_PLAYER = '@'

class PinLayout:
    def __init__(self):
        self.player_spot = None
        self.monster_spots = []
        #
        self.chart_ground = None    # water, land
        self.chart_mobile = None    # mangrove, monster, player
        self.chart_composite = None
        self.is_ready = False
    def on_init(self, height, width):
        self.chart_ground = chart_new(
            height=height,
            width=width)
        self.chart_mobile = chart_new(
            height=height,
            width=width)
        self.chart_composite = chart_new(
            height=height,
            width=width)
    def on_terrain_water(self, drop, rest):
        self.chart_ground.put(
            spot=(drop, rest),
            c=SIGIL_WATER)
    def on_terrain_land(self, drop, rest):
        self.chart_ground.put(
            spot=(drop, rest),
            c=SIGIL_LAND)
    def on_terrain_mangrove(self, drop, rest):
        self.chart_mobile.put(
            spot=(drop, rest),
            c=SIGIL_MANGROVE)
    def on_terrain_done(self):
        self.is_ready = True
    #
    def get_chart(self):
        'Returns [ (spot, c) ]'
        for (spot, c) in self.chart_ground.get():
            if c == SIGIL_VOID:
                continue
            self.chart_composite.put(
                spot=spot,
                c=c)
        for (spot, c) in self.chart_mobile.get():
            if c == SIGIL_VOID:
                continue
            self.chart_composite.put(
                spot=spot,
                c=c)
        return self.chart_composite.get()

class CogLadyOfTheLake:
    '''
    The lady is responsible for:
    * Setting up the swamp
    * Controlling the monsters inside it
    '''
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.pin_layout = orb.init_pin(PinLayout)
        self.monsters = []
    def on_order_monster_turn(self):
        if random.random() > 0.8:
            self._create_monster()
    #
    def _create_monster(self):
        log('xxx create monster')

class CogView:
    '''
    The view is responsible for detecting changes to the board, and updating
    the world as to the changes after each of the lady's move.

    Separately, a full refresh is needed at the beginning of the game than
    periodically after that. The view does this also.
    '''
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.chart = None
        self.board = None
        self.pin_layout = orb.init_pin(PinLayout)
    def on_init(self, height, width):
        swamp = swamp_new(
            height=height,
            width=width)
        chart = chart_new(
            height=height,
            width=width)
        swamp.populate_chart(
            chart=chart)
        for (spot, c) in chart.get():
            (drop, rest) = spot
            if c == '~':
                self.nearcast.terrain_water(
                    drop=drop,
                    rest=rest)
            elif c == '.':
                self.nearcast.terrain_land(
                    drop=drop,
                    rest=rest)
            elif c == '%':
                self.nearcast.terrain_mangrove(
                    drop=drop,
                    rest=rest)
            else:
                raise Exception("Unrecognised terrain [%s]"%c)
        self.nearcast.terrain_done()
    def on_terrain_done(self):
        self.nearcast.full_refresh()
    def on_full_refresh(self):
        if not self.pin_layout.is_ready:
            return
        self.nearcast.display_clear()
        for (spot, c) in self.pin_layout.get_chart():
            (drop, rest) = spot
            log('here %s %s'%(str(drop), str(rest)))
            if c == SIGIL_WATER:
                self.nearcast.display_put(
                    drop=drop,
                    rest=rest,
                    s=c,
                    cpair=e_colpair.blue_t)
            elif c == SIGIL_LAND:
                self.nearcast.display_put(
                    drop=drop,
                    rest=rest,
                    s=c,
                    cpair=e_colpair.white_t)
            elif c == SIGIL_PLAYER:
                self.nearcast.display_put(
                    drop=drop,
                    rest=rest,
                    s=c,
                    cpair=e_colpair.yellow_t)
            elif c == SIGIL_MANGROVE:
                self.nearcast.display_put(
                    drop=drop,
                    rest=rest,
                    s=c,
                    cpair=e_colpair.green_t)
            elif c == SIGIL_MONSTER:
                self.nearcast.display_put(
                    drop=drop,
                    rest=rest,
                    s=c,
                    cpair=e_colpair.red_t)
            else:
                self.nearcast.display_put(
                    drop=drop,
                    rest=rest,
                    s='x',
                    cpair=e_colpair.red_t)

class CogPlayer:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.pin_display_mode = orb.init_pin(PinDisplayMode)
    def on_input_nw(self):
        self.nearcast.order_monster_turn()
    def on_input_nn(self):
        self.nearcast.order_monster_turn()
    def on_input_ne(self):
        self.nearcast.order_monster_turn()
    def on_input_sw(self):
        self.nearcast.order_monster_turn()
    def on_input_ss(self):
        self.nearcast.order_monster_turn()
    def on_input_se(self):
        self.nearcast.order_monster_turn()
    def on_input_ww(self):
        self.nearcast.order_monster_turn()
    def on_input_ee(self):
        self.nearcast.order_monster_turn()

class CogBridge:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
    def set_callbacks(self, cb_cls, cb_put, cb_box):
        self.cb_cls = cb_cls
        self.cb_put = cb_put
        self.cb_box = cb_box
    def nc_init(self, height, width):
        self.nearcast.init(
            height=height,
            width=width)
    def nc_input_nw(self):
        self.nearcast.input_nw()
    def nc_input_nn(self):
        self.nearcast.input_nn()
    def nc_input_ne(self):
        self.nearcast.input_ne()
    def nc_input_sw(self):
        self.nearcast.input_sw()
    def nc_input_ss(self):
        self.nearcast.input_ss()
    def nc_input_ww(self):
        self.nearcast.input_ww()
    def nc_input_ee(self):
        self.nearcast.input_ee()
    def nc_input_se(self):
        self.nearcast.input_se()
    def nc_input_bump(self):
        self.nearcast.input_bump()
    def nc_full_refresh(self):
        self.nearcast.full_refresh()
    #
    def on_box_display(self, message):
        self.cb_box(
            message=message)
    def on_display_clear(self):
        self.cb_cls()
    def on_display_put(self, drop, rest, s, cpair):
        self.cb_put(
            drop=drop,
            rest=rest,
            s=s,
            cpair=cpair)

class SpinSwampMonster:
    def __init__(self, engine, height, width, cb_cls, cb_put, cb_box):
        self.engine = engine
        self.height = height
        self.width = width
        self.cb_cls = cb_cls
        self.cb_put = cb_put
        self.cb_box = cb_box
        #
        self.nearcast = nearcast_schema_new(
            i_nearcast=I_NEARCAST)
        self.orb = self.engine.init_orb(
            orb_h='swamp_monster_orb',
            nearcast_schema=self.nearcast)
        self.orb.add_log_snoop()
        self.orb.init_cog(CogLadyOfTheLake)
        self.orb.init_cog(CogView)
        self.orb.init_cog(CogPlayer)
        #
        self.bridge = self.orb.init_cog(CogBridge)
        self.bridge.set_callbacks(
            cb_cls=cb_cls,
            cb_put=cb_put,
            cb_box=cb_box)
        self.bridge.nc_init(
            height=self.height,
            width=self.width)
    def input_nw(self):
        self.bridge.nc_input_nw()
    def input_nn(self):
        self.bridge.nc_input_nn()
    def input_ne(self):
        self.bridge.nc_input_ne()
    def input_sw(self):
        self.bridge.nc_input_sw()
    def input_ss(self):
        self.bridge.nc_input_ss()
    def input_se(self):
        self.bridge.nc_input_se()
    def input_ww(self):
        self.bridge.nc_input_ww()
    def input_ee(self):
        self.bridge.nc_input_ee()
    def input_bump(self):
        self.bridge.nc_input_bump()
    def full_refresh(self):
        self.bridge.nc_full_refresh()

def spin_swamp_monster_new(engine, height, width, cb_cls, cb_put, cb_box):
    '''
    cb_cls()
        # clear screen

    cb_put(drop, rest, s, cpair)

    cb_box(s)
        # message box
    '''
    ob = SpinSwampMonster(
        engine=engine,
        height=height,
        width=width,
        cb_cls=cb_cls,
        cb_put=cb_put,
        cb_box=cb_box)
    return ob

