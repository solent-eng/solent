#
# spin_simple
#
# // overview
# Simple game developed as part of the evolution of roguebox.
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

from solent import e_cpair
from solent.console import cgrid_new
from solent.eng import nearcast_schema_new
from solent.log import log
from solent.rogue import directive_new

from collections import deque
import random
import time

I_NEARCAST = '''
    i message h
        i field h

    message init
        field grid_height
        field grid_width
'''

DIRECTIVE_HELP = directive_new('help', 'show help message')
DIRECTIVE_BUMP = directive_new('bump', 'bring up a menu')
DIRECTIVE_NW = directive_new('nw', 'move/act in this direction')
DIRECTIVE_NN = directive_new('nn', 'move/act in this direction')
DIRECTIVE_NE = directive_new('ne', 'move/act in this direction')
DIRECTIVE_SW = directive_new('sw', 'move/act in this direction')
DIRECTIVE_SS = directive_new('ss', 'move/act in this direction')
DIRECTIVE_SE = directive_new('se', 'move/act in this direction')
DIRECTIVE_WW = directive_new('ww', 'move/act in this direction')
DIRECTIVE_EE = directive_new('ee', 'move/act in this direction')

HELP = '''Hit things with your crowbar. Survive.

Movement:
 q w e      7 8 9       y k u
 a   d      4   6       h   l
 z x d      1 2 3       b j n

Command:
   s          5         space

Tab returns to the main menu.
'''

PAIR_WALL = ('.', e_cpair.blue_t)
PAIR_PLAYER = ('@', e_cpair.yellow_t)
PAIR_WEED = ('t', e_cpair.red_t)

class CogBridge:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
    def set_callbacks(self):
        pass
    def nc_init(self, grid_height, grid_width):
        self.nearcast.init(
            grid_height=grid_height,
            grid_width=grid_width)

class SpinSimple:
    def __init__(self, engine, grid_height, grid_width, cb_ready_alert, cb_grid_alert, cb_mail_alert, cb_over_alert):
        self.engine = engine
        self.grid_height = grid_height
        self.grid_width = grid_width
        self.cb_grid_alert = cb_grid_alert
        self.cb_mail_alert = cb_mail_alert
        self.cb_ready_alert = cb_ready_alert
        self.cb_over_alert = cb_over_alert

        self.turn = 0
        self.b_game_alive = False

        #
        # coordinate pools
        self.cpool_spare = None
        self.cpool_wall = None
        self.cpool_player = None
        self.cpool_weed = None

        self.supported_directives = None
        self._init_supported_directives()

        self.cgrid = cgrid_new(
            height=grid_height,
            width=grid_width)
        self.q_mail_messages = deque()

        self.nearcast = None
        self._init_nearcast()

        self.orb = None
        self._init_orb()

        self.bridge = self.orb.init_cog(CogBridge)
        self.bridge.set_callbacks()

        self.bridge.nc_init(
            grid_height=self.grid_height,
            grid_width=self.grid_width)

    def _init_supported_directives(self):
        self.supported_directives = [
            globals()[key] for key
            in globals().keys()
            if key.startswith('DIRECTIVE_')]

    def _init_nearcast(self):
        self.nearcast = nearcast_schema_new(
            i_nearcast=I_NEARCAST)

    def _init_orb(self):
        self.orb = self.engine.init_orb(
            orb_h='swamp_monster_orb',
            nearcast_schema=self.nearcast)
        self.orb.add_log_snoop()

    def get_supported_directives(self):
        '''
        Returns list of instances of solent.rogue.directive representing
        the directives that this instance cares about. The reason for this
        design is that it allows the container to handle input configuration.
        For example, if you want the number 7 to mean north-east, you will
        want to be able to configure that. And it would be a distraction from
        the game engine itself.
        '''
        return self.supported_directives[:]

    def new_game(self):
        self.turn = 0
        self.b_game_alive = True

        self._zero_coord_pools()
        self._create_board()

        self.cb_ready_alert()

        self._announce("You are in the garden. Eliminate those evil weeds!")
        self._announce("[Press ? for help]")

    def _zero_coord_pools(self):
        self.cpool_spare = []
        self.cpool_wall = []
        self.cpool_player = []
        self.cpool_weed = []
        for drop in range(self.grid_height):
            for rest in range(self.grid_width):
                self.cpool_spare.append( (drop, rest) )

    def get_turn(self):
        return self.turn

    def get_cgrid(self, cgrid, nail, peri):
        self._render_cgrid()
        cgrid.blit(
            src_cgrid=self.cgrid,
            nail=nail,
            peri=peri)

    def retrieve_mail(self):
        l = []
        while self.q_mail_messages:
            l.append(self.q_mail_messages.popleft())
        return l

    def directive(self, directive_h):
        if directive_h == 'help':
            for line in HELP.split('\n'):
                self._announce(line)
            return
        if False == self.b_game_alive:
            return
        if directive_h == 'bump':
            pass
        else:
            self.turn += 1

            player_spot = self.cpool_player[0]
            target_spot = list(player_spot)
            if directive_h in 'nw|ww|sw'.split('|'):
                target_spot[1] -= 1
            if directive_h in 'ne|ee|se'.split('|'):
                target_spot[1] += 1
            if directive_h in 'nw|nn|ne'.split('|'):
                target_spot[0] -= 1
            if directive_h in 'sw|ss|se'.split('|'):
                target_spot[0] += 1
            self._player_move(
                player_spot=player_spot,
                target_spot=tuple(target_spot))
            if 0 == len(self.cpool_weed):
                self._announce('You win!')
                self._game_over()

    def _player_move(self, player_spot, target_spot):
        if target_spot in self.cpool_spare:
            self.cpool_player.remove(player_spot)
            self.cpool_spare.append(player_spot)
            self.cpool_spare.remove(target_spot)
            self.cpool_player.append(target_spot)
            self.cb_grid_alert()
            return
        elif target_spot in self.cpool_weed:
            self._announce(
                message='You slash angrily at the weed!')
            self.cpool_player.remove(player_spot)
            self.cpool_spare.append(player_spot)
            self.cpool_weed.remove(target_spot)
            self.cpool_player.append(target_spot)
            self.cb_grid_alert()

    def _announce(self, message):
        self.q_mail_messages.append(message)
        self.cb_mail_alert()

    def _game_over(self):
        self.b_game_alive = False
        self.cb_over_alert()

    def _create_board(self):
        coord = ( int(self.grid_height/2), int(self.grid_width/2) )
        self.cpool_spare.remove(coord)
        self.cpool_player.append(coord)

        # place walls
        for rest in range(32, 48):
            coord = (6, rest)
            self.cpool_spare.remove(coord)
            self.cpool_wall.append(coord)
            coord = (18, rest)
            self.cpool_spare.remove(coord)
            self.cpool_wall.append(coord)
        for drop in range(7, 18):
            coord = (drop, 32)
            log('coord %s'%(str(coord)))
            self.cpool_spare.remove(coord)
            self.cpool_wall.append(coord)
            coord = (drop, 47)
            self.cpool_spare.remove(coord)
            self.cpool_wall.append(coord)

        # place weeds. we need at least one.
        while not self.cpool_weed:
            for coord in self.cpool_spare:
                (drop, rest) = coord
                if drop < 8 or drop > 16:
                    continue
                if rest < 34 or rest > 46:
                    continue
                if random.random() > 0.98:
                    self.cpool_spare.remove(coord)
                    self.cpool_weed.append(coord)

    def _render_cgrid(self):
        self.cgrid.clear()
        for coord in self.cpool_wall:
            (drop, rest) = coord
            (c, cpair) = PAIR_WALL
            self.cgrid.put(
                drop=drop,
                rest=rest,
                s=c,
                cpair=cpair)
        for coord in self.cpool_player:
            (drop, rest) = coord
            (c, cpair) = PAIR_PLAYER
            if not self.b_game_alive:
                cpair = e_cpair.purple_t
            self.cgrid.put(
                drop=drop,
                rest=rest,
                s=c,
                cpair=cpair)
        for coord in self.cpool_weed:
            (drop, rest) = coord
            (c, cpair) = PAIR_WEED
            self.cgrid.put(
                drop=drop,
                rest=rest,
                s=c,
                cpair=cpair)

def spin_simple_new(engine, grid_height, grid_width, cb_ready_alert, cb_grid_alert, cb_mail_alert, cb_over_alert):
    '''
    cb_grid_alert. No arguments. This is called whenver the grid has been
    updated. The container will probably want to know the difference between
    updates and no updates, but will probably not want to display every
    update. They can get the current grid with get_grid.

    cb_mail_alert. No arguments. This is called whenever a new mail message
    is waiting (e.g. status messages, but mail is fewer characters). The
    container then knows to run a collect at the next appropriate time. They
    can get new mail with get_mail

    cb_ready_alert. No arguments. This is called to notify the container that
    a new game is ready. Typically, this would be some time after a call to
    new_game.

    cb_over_alert. No arguments. Tells the container that we are at 'game
    over'.
    '''
    ob = SpinSimple(
        engine=engine,
        grid_height=grid_height,
        grid_width=grid_width,
        cb_ready_alert=cb_ready_alert,
        cb_grid_alert=cb_grid_alert,
        cb_mail_alert=cb_mail_alert,
        cb_over_alert=cb_over_alert)
    return ob
