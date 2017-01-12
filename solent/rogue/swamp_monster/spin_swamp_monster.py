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
from .meep import meep_new
from .sigil import sigil_new
from .swamp_generator import swamp_generator_new

from solent import e_colpair
from solent.eng import nearcast_schema_new
from solent.log import log
from solent.util import uniq

from collections import OrderedDict as od
import random

I_NEARCAST = '''
    i message h
        i field h

    # - static data ------------------------------------------
    message sigil
        field h
        field c
        field cpair

    # - init -------------------------------------------------
    message init
        field height
        field width

    # - runtime vectors --------------------------------------
    message request_full_refresh

    message display_clear
    message display_put
        field drop
        field rest
        field s
        field cpair

    message tile
        field drop
        field rest
        field sigil_h
        field b_is_land

    message meep
        field h
        field drop
        field rest
        field sigil_h
        field b_is_player

    message game_start
    message game_over

    message input_nw
    message input_nn
    message input_ne
    message input_sw
    message input_ss
    message input_se
    message input_ww
    message input_ee
    message input_bump

    message meep_move
        field meep_h
        field drop
        field rest

    message player_turn_done
    message lady_turn_done

    # - implement later --------------------------------------
    message box_display
        field message
'''

SIGIL_H_LAND = uniq()
SIGIL_H_MANGROVE = uniq()
SIGIL_H_MONSTER = uniq()
SIGIL_H_PLAYER = uniq()
SIGIL_H_VOID = uniq()
SIGIL_H_WATER = uniq()

class PinSigils:
    '''
    Keeps track of static data spun to represent sigils.
    '''
    def __init__(self, orb):
        self.orb = orb
        #
        self.d = {}
    #
    def on_sigil(self, h, c, cpair):
        self.d[h] = sigil_new(
            h=h,
            c=c,
            cpair=cpair)
    #
    def get(self, sigil_h):
        return self.d[sigil_h]

class PinGameState:
    def __init__(self, orb):
        self.orb = orb
        #
        self.has_game_started = False
        self.is_game_open = False
    def on_game_start(self):
        self.has_game_started = True
        self.is_game_open = True
    def on_game_over(self):
        self.is_game_open = False

class PinTiles:
    '''
    Keeps track of the layout of the board. This could be useful for multiple
    scenarios: display, planning action for AIs, validating player input.
    '''
    def __init__(self, orb):
        self.orb = orb
        #
        self.chart = None
    def on_init(self, height, width):
        self.chart = chart_new(
            height=height,
            width=width)
    def on_tile(self, drop, rest, sigil_h, b_is_land):
        self.chart.put(
            spot=(drop, rest),
            sigil_h=sigil_h)
    #
    def get_chart(self):
        return self.chart

class PinMeeps:
    def __init__(self, orb):
        self.orb = orb
        #
        self.pin_sigils = orb.init_pin(PinSigils)
        self.d_meeps = od()
        self.chart = None
    def on_init(self, height, width):
        self.chart = chart_new(
            height=height,
            width=width)
    def on_meep(self, h, drop, rest, sigil_h, b_is_player):
        self.d_meeps[h] = meep_new(
            h=h,
            drop=drop,
            rest=rest,
            sigil_h=sigil_h,
            b_is_player=b_is_player)
        self.chart.put(
            spot=(drop, rest),
            sigil_h=sigil_h)
    def on_meep_move(self, meep_h, drop, rest):
        meep = self.d_meeps[meep_h]
        meep.drop = drop
        meep.rest = rest
        self.chart.rm(
            spot=(meep.drop, meep.rest))
        self.chart.put(
            spot=(meep.drop, meep.rest),
            sigil=meep.sigil_h)
    #
    def get_chart(self):
        return self.chart
    def list(self):
        '''Returns list of Meep'''
        return self.d_meeps.values()
    def get(self, h):
        return self.d_meeps[h]
    def meep_at(self, drop, rest):
        for meep in self.d_meeps.values():
            if meep.drop == drop and meep.rest == rest:
                return meep
        return None

class CogWorld:
    '''
    This is responsible for two things:
    * Generating the world
    * Updating the display with a perspective

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
        self.height = None
        self.width = None
        self.chart = None
        self.pin_game_state = orb.init_pin(PinGameState)
        self.pin_sigils = orb.init_pin(PinSigils)
        self.pin_tiles = orb.init_pin(PinTiles)
        self.pin_meeps = orb.init_pin(PinMeeps)
    def on_init(self, height, width):
        self.height = height
        self.width = width
        #
        self.chart = chart_new(
            height=height,
            width=width)
        self._tile_placement()
        self._player_placement()
        self._mangrove_placement()
        self.nearcast.game_start()
    def on_game_start(self):
        self._send_clean_display()
    def on_request_full_refresh(self):
        if self.pin_game_state.has_game_started:
            self._send_clean_display()
    #
    def _tile_placement(self):
        swamp_generator = swamp_generator_new(
            height=self.height,
            width=self.width)
        grid = swamp_generator.get_grid()
        del swamp_generator
        sigil_land = self.pin_sigils.get(SIGIL_H_LAND)
        sigil_water = self.pin_sigils.get(SIGIL_H_WATER)
        for (drop, row) in enumerate(grid):
            for (rest, cell_word) in enumerate(row):
                if cell_word == 'water':
                    sigil_h = SIGIL_H_WATER
                    b_is_land = 'n'
                elif cell_word == 'land':
                    sigil_h = SIGIL_H_LAND
                    b_is_land = 'y'
                else:
                    raise Exception("Unrecognised word [%s]"%(cell_word))
                self.nearcast.tile(
                    drop=drop,
                    rest=rest,
                    sigil_h=sigil_h,
                    b_is_land=b_is_land)
    def _player_placement(self):
        drop = self.height / 2
        rest = self.width / 2
        self.nearcast.meep(
            h='@',
            drop=drop,
            rest=rest,
            sigil_h=SIGIL_H_PLAYER,
            b_is_player=True)
    def _mangrove_placement(self):
        # ! remember not to place a mangrove in the centre of the board,
        # because that is where the player will be.
        log('xxx mangrove placement')
        '''
        field h
        field sigil_h
        field drop
        field rest
        field b_is_player
        '''
    def _send_clean_display(self):
        self.nearcast.display_clear()
        self.chart.blit(
            chart=self.pin_tiles.get_chart())
        self.chart.blit(
            chart=self.pin_meeps.get_chart())
        for (spot, sigil_h) in self.chart.items():
            (drop, rest) = spot
            sigil = self.pin_sigils.get(
                sigil_h=sigil_h)
            self.nearcast.display_put(
                drop=drop,
                rest=rest,
                s=sigil.c,
                cpair=sigil.cpair)

class CogPlayer:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
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
        self.pin_tiles = orb.init_pin(PinTiles)
        self.monsters = []

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
    def nc_sigil(self, h, c, cpair):
        self.nearcast.sigil(
            h=h,
            c=c,
            cpair=cpair)
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
    def nc_request_full_refresh(self):
        self.nearcast.request_full_refresh()
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
        self.orb.init_cog(CogWorld)
        self.orb.init_cog(CogLadyOfTheLake)
        self.orb.init_cog(CogPlayer)
        #
        self.bridge = self.orb.init_cog(CogBridge)
        self.bridge.set_callbacks(
            cb_cls=cb_cls,
            cb_put=cb_put,
            cb_box=cb_box)
        #
        self._send_static_data()
        #
        self.bridge.nc_init(
            height=self.height,
            width=self.width)
    def _send_static_data(self):
        self.bridge.nc_sigil(
            h=SIGIL_H_LAND,
            c='.',
            cpair=e_colpair.white_t)
        self.bridge.nc_sigil(
            h=SIGIL_H_MANGROVE,
            c='%',
            cpair=e_colpair.green_t)
        self.bridge.nc_sigil(
            h=SIGIL_H_MONSTER,
            c='Y',
            cpair=e_colpair.red_t)
        self.bridge.nc_sigil(
            h=SIGIL_H_PLAYER,
            c='@',
            cpair=e_colpair.yellow_t)
        self.bridge.nc_sigil(
            h=SIGIL_H_VOID,
            c=' ',
            cpair=e_colpair.white_t)
        self.bridge.nc_sigil(
            h=SIGIL_H_WATER,
            c='~',
            cpair=e_colpair.blue_t)
    #
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
        self.bridge.nc_request_full_refresh()

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

