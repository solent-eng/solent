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

from solent import solent_cpair
from solent import uniq
from solent.log import log

from collections import deque
from collections import OrderedDict as od
import random
import time

I_NEARCAST = '''
    i message h
        i field h

    # - static data ------------------------------------------
    message sigil
        field h
        field c
        field cpair

    message etype
        # types of meep

    # - init -------------------------------------------------
    message init
        field height
        field width

    # - runtime vectors --------------------------------------
    message request_full_refresh

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

    message status_message
        field s
    message game_start
    message game_over

    message need_input
    message input
        field directive

    message meep_move
        field meep_h
        field drop
        field rest
    message meep_death
        field meep_h

    message turn_player
    message turn_lady
    message turn_done

    # - implement later --------------------------------------
    message box_display
        field s
'''

DIRECTIVE_NW = uniq()
DIRECTIVE_NN = uniq()
DIRECTIVE_NE = uniq()
DIRECTIVE_SW = uniq()
DIRECTIVE_SS = uniq()
DIRECTIVE_SE = uniq()
DIRECTIVE_WW = uniq()
DIRECTIVE_EE = uniq()
DIRECTIVE_BUMP = uniq()

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
    def exists(self, sigil_h):
        return sigil_h in self.d
    def get(self, sigil_h):
        return self.d[sigil_h]
    def c_to_sigil_h(self, c):
        speculative_sigil_h = 'char_%s'%(ord(c))
        if speculative_sigil_h in self.d:
            return speculative_sigil_h
        else:
            # underscore
            return 'char_95'

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
        self.player_meep = None
        self.chart = None
    def on_init(self, height, width):
        self.chart = chart_new(
            height=height,
            width=width)
    def on_meep(self, h, drop, rest, sigil_h, b_is_player):
        meep = meep_new(
            h=h,
            drop=drop,
            rest=rest,
            sigil_h=sigil_h,
            b_is_player=b_is_player)
        if b_is_player:
            self.player_meep = meep
        self.d_meeps[h] = meep
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
    def get_player_meep(self):
        return self.player_meep
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

class PinStatusMessages:
    def __init__(self, orb):
        self.orb = orb
        #
        self.q_log = deque()
        self.chart = None
        self.pin_sigils = orb.init_pin(PinSigils)
    def on_init(self, height, width):
        self.chart = chart_new(
            height=height,
            width=width)
    def on_status_message(self, s):
        now100 = time.time() * 100
        #
        self.q_log.append( (s, now100) )
        if len(self.q_log) > 100:
            self.q_log.popleft()
    #
    def get_chart(self):
        self.chart.clear()
        # Ugh. Here we individually convert each sigil in the status bar into
        # a sigil, and then place that on the chart.
        for (drop, line) in enumerate(self._get_recent_entries()):
            for (rest, c) in enumerate(line):
                sigil_h = self.pin_sigils.c_to_sigil_h(c)
                self.chart.put(
                    spot=(drop, rest),
                    sigil_h = sigil_h)
        return self.chart
    #
    def _get_recent_entries(self, count=3):
        nail = len(self.q_log) - (count)
        if nail < 0:
            nail = 0
        peri = len(self.q_log)
        sb = []
        while nail < peri:
            log('nail %s peri %s'%(nail, peri)) # xxx
            sb.append(self.q_log[nail][0])
            nail += 1
        return sb

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
        self.pin_game_state = orb.init_pin(PinGameState)
        self.pin_sigils = orb.init_pin(PinSigils)
        self.pin_tiles = orb.init_pin(PinTiles)
        self.pin_meeps = orb.init_pin(PinMeeps)
        self.pin_status_messages = orb.init_pin(PinStatusMessages)
        #
        self.chart_log = None
        self.chart_board = None
        #
        # We double-buffer by using two charts. This allows us to track diffs
        # and be conservative in only sending out updates
        self.chart_buffer = None
        self.chart_buffer_prev = None
        #
        self.need_to_update_display = False
    def at_turn(self, activity):
        if self.need_to_update_display:
            activity.mark(
                l=self,
                s='need to update display')
            self._send_display_update()
            self.need_to_update_display = False
    #
    def on_init(self, height, width):
        self.height = height
        self.width = width
        #
        self.chart_log = chart_new(
            height=height,
            width=width)
        self.chart_board = chart_new(
            height=height,
            width=width)
        self.chart_buffer = chart_new(
            height=height,
            width=width)
        self.chart_buffer_prev = chart_new(
            height=height,
            width=width)
        #
        self._tile_placement()
        self._player_placement()
        self._mangrove_placement()
        self.nearcast.game_start()
    def on_request_full_refresh(self):
        if not self.pin_game_state.has_game_started:
            return
        self._send_clean_display()
    def on_game_start(self):
        self._send_clean_display()
        self.nearcast.turn_player()
    def on_turn_player(self):
        pass
    def on_turn_done(self):
        self._send_display_update()
    def on_input(self, directive):
        self.need_to_update_display = True
    def on_status_message(self, s):
        self.need_to_update_display = True
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
    def _build_chart(self):
        self.chart_buffer_prev.blit(self.chart_buffer)
        #
        self.chart_buffer.blit(
            chart=self.pin_tiles.get_chart())
        self.chart_buffer.blit(
            chart=self.pin_meeps.get_chart())
        self.chart_buffer.blit(
            chart=self.pin_status_messages.get_chart())
    def _send_clean_display(self):
        if not self.pin_game_state.has_game_started:
            return
        self._build_chart()
        log('len %s'%(len(self.chart_buffer)))
        for (spot, sigil_h) in self.chart_buffer.items():
            (drop, rest) = spot
            sigil = self.pin_sigils.get(
                sigil_h=sigil_h)
            self.nearcast.display_put(
                drop=drop,
                rest=rest,
                s=sigil.c,
                cpair=sigil.cpair)
    def _send_display_update(self):
        if not self.pin_game_state.has_game_started:
            return
        self._build_chart()
        diff = self.chart_buffer.show_differences_to(
            chart=self.chart_buffer_prev)
        for (spot, sigil_h) in diff:
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
        #
        self.pin_game_state = orb.init_pin(PinGameState)
        self.pin_meeps = orb.init_pin(PinMeeps)
        self.q_input = deque()
        self.sent_need_input = False
    def at_turn(self, activity):
        if self.q_input:
            activity.mark(
                l=self,
                s='process player turn')
            self._attempt_turn(
                directive=self.q_input.popleft())
        else:
            if not self.sent_need_input:
                self.nearcast.need_input()
                self.sent_need_input = True
    def on_input(self, directive):
        self._buffer_input(directive)
        #
        # xxx
        if directive == DIRECTIVE_EE:
            self.nearcast.status_message(
                s='status %s'%(time.time()))
    #
    def _buffer_input(self, directive):
        self.sent_need_input = False
        self.q_input.append(directive)
    def _attempt_turn(self, directive):
        player_meep = self.pin_meeps.get_player_meep()
        #
        # work out where we are going to
        to_drop = player_meep.drop
        to_rest = player_meep.rest
        if directive in (DIRECTIVE_NW, DIRECTIVE_NN, DIRECTIVE_NE):
            to_drop -= 1
        if directive in (DIRECTIVE_SW, DIRECTIVE_SS, DIRECTIVE_SE):
            to_drop += 1
        if directive in (DIRECTIVE_NW, DIRECTIVE_WW, DIRECTIVE_SW):
            to_rest -= 1
        if directive in (DIRECTIVE_NE, DIRECTIVE_EE, DIRECTIVE_SE):
            to_rest += 1
        #
        # if there is a meep there, we are attacking it
        to_meep = self.pin_meeps.meep_at(
            drop=to_drop,
            rest=to_rest)
        if None != to_meep:
            self.nearcast.meep_death(
                meep_h=to_meep.h)
            return
        #
        # if there is water there, we can't move to it.

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
    def set_callbacks(self, cb_cls, cb_put, cb_log):
        self.cb_cls = cb_cls
        self.cb_put = cb_put
        self.cb_log = cb_log
    def nc_init(self, height, width):
        self.nearcast.init(
            height=height,
            width=width)
    def nc_sigil(self, h, c, cpair):
        self.nearcast.sigil(
            h=h,
            c=c,
            cpair=cpair)
    def nc_input(self, directive):
        self.nearcast.input(
            directive=directive)
    def nc_request_full_refresh(self):
        self.nearcast.request_full_refresh()
    #
    def on_display_put(self, drop, rest, s, cpair):
        self.cb_put(
            drop=drop,
            rest=rest,
            s=s,
            cpair=cpair)

class SpinSwampMonster:
    def __init__(self, engine, height, width, cb_cls, cb_put, cb_log):
        self.engine = engine
        self.height = height
        self.width = width
        self.cb_cls = cb_cls
        self.cb_put = cb_put
        self.cb_log = cb_log
        #
        self.orb = self.engine.init_orb(
            spin_h='swamp_monster_orb',
            i_nearcast=I_NEARCAST)
        self.orb.add_log_snoop()
        self.orb.init_cog(CogWorld)
        self.orb.init_cog(CogLadyOfTheLake)
        self.orb.init_cog(CogPlayer)
        #
        self.bridge = self.orb.init_cog(CogBridge)
        self.bridge.set_callbacks(
            cb_cls=cb_cls,
            cb_put=cb_put,
            cb_log=cb_log)
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
            cpair=solent_cpair('white'))
        self.bridge.nc_sigil(
            h=SIGIL_H_MANGROVE,
            c='%',
            cpair=solent_cpair('green'))
        self.bridge.nc_sigil(
            h=SIGIL_H_MONSTER,
            c='Y',
            cpair=solent_cpair('red'))
        self.bridge.nc_sigil(
            h=SIGIL_H_PLAYER,
            c='@',
            cpair=solent_cpair('yellow'))
        self.bridge.nc_sigil(
            h=SIGIL_H_VOID,
            c=' ',
            cpair=solent_cpair('white'))
        self.bridge.nc_sigil(
            h=SIGIL_H_WATER,
            c='~',
            cpair=solent_cpair('blue'))
        #
        # Hilarity. Due to an oversight in the way I've designed the current
        # interation of the rogue game, it is necessary to translate status bar
        # messages into lists of sigils. That is what this class does.
        for i in range(0x20, 0x7e):
            c = chr(i)
            self.bridge.nc_sigil(
                h='char_%s'%i,
                c=c,
                cpair=solent_cpair('teal'))
    #
    def input_nw(self):
        self.bridge.nc_input(
            directive=DIRECTIVE_NW)
    def input_nn(self):
        self.bridge.nc_input(
            directive=DIRECTIVE_NN)
    def input_ne(self):
        self.bridge.nc_input(
            directive=DIRECTIVE_NE)
    def input_sw(self):
        self.bridge.nc_input(
            directive=DIRECTIVE_SW)
    def input_ss(self):
        self.bridge.nc_input(
            directive=DIRECTIVE_SS)
    def input_se(self):
        self.bridge.nc_input(
            directive=DIRECTIVE_SE)
    def input_ww(self):
        self.bridge.nc_input(
            directive=DIRECTIVE_WW)
    def input_ee(self):
        self.bridge.nc_input(
            directive=DIRECTIVE_EE)
    def input_bump(self):
        self.bridge.nc_input(
            directive=DIRECTIVE_BUMP)
    def full_refresh(self):
        self.bridge.nc_request_full_refresh()

def spin_swamp_monster_new(engine, height, width, cb_cls, cb_put, cb_log):
    '''
    cb_cls()
        # clear screen

    cb_put(drop, rest, s, cpair)

    cb_log(s)
        # send a message, such as to the status bar
    '''
    ob = SpinSwampMonster(
        engine=engine,
        height=height,
        width=width,
        cb_cls=cb_cls,
        cb_put=cb_put,
        cb_log=cb_log)
    return ob

