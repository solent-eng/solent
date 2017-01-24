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
        field height
        field width
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
PAIR_ZOMBIE = ('z', e_cpair.red_t)

class CogBridge:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
    def set_callbacks(self):
        pass
    def nc_init(self, height, width):
        self.nearcast.init(
            height=height,
            width=width)

class SpinSimple:
    def __init__(self, engine, height, width, cb_ready_alert, cb_grid_alert, cb_mail_alert, cb_over_alert):
        self.engine = engine
        self.height = height
        self.width = width
        self.cb_grid_alert = cb_grid_alert
        self.cb_mail_alert = cb_mail_alert
        self.cb_ready_alert = cb_ready_alert
        self.cb_over_alert = cb_over_alert

        self.turn = 0

        #
        # coordinate pools
        self.cpool_spare = None
        self._init_coord_pool_spare()
        self.cpool_wall = []
        self.cpool_player = []
        self.cpool_zombie = []

        self.supported_directives = None
        self._init_supported_directives()

        self.cgrid = cgrid_new(
            height=height,
            width=width)
        self.q_mail_messages = deque()

        self.nearcast = None
        self._init_nearcast()

        self.orb = None
        self._init_orb()

        self.bridge = self.orb.init_cog(CogBridge)
        self.bridge.set_callbacks()

        self.bridge.nc_init(
            height=self.height,
            width=self.width)

    def _init_coord_pool_spare(self):
        self.cpool_spare = []
        for drop in range(self.height):
            for rest in range(self.width):
                self.cpool_spare.append( (drop, rest) )

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
        self._create_board()
        # At the moment, there's nothing to be done, so we just call this.
        # In future, this function will move away from here.
        self.cb_ready_alert()
        self._queue_mail("[Press ? for help]")

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
                self._queue_mail(line)
        elif directive_h == 'bump':
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
            self._move_player(
                player_spot=player_spot,
                target_spot=tuple(target_spot))

    def _move_player(self, player_spot, target_spot):
        if target_spot not in self.cpool_spare:
            return
        self.cpool_player.remove(player_spot)
        self.cpool_spare.append(player_spot)
        self.cpool_spare.remove(target_spot)
        self.cpool_player.append(target_spot)
        self.cb_grid_alert()

    def _queue_mail(self, message):
        self.q_mail_messages.append(message)
        self.cb_mail_alert()

    def _create_board(self):
        coord = ( int(self.height/2), int(self.width/2) )
        self.cpool_spare.remove(coord)
        self.cpool_player.append(coord)

        for rest in range(self.width):
            coord = (0, rest)
            self.cpool_spare.remove(coord)
            self.cpool_wall.append(coord)
            coord = (self.height-1, rest)
            self.cpool_spare.remove(coord)
            self.cpool_wall.append(coord)
        for drop in range(1, self.height-1):
            coord = (drop, 0)
            self.cpool_spare.remove(coord)
            self.cpool_wall.append(coord)
            coord = (drop, self.width-1)
            self.cpool_spare.remove(coord)
            self.cpool_wall.append(coord)

        for coord in self.cpool_spare:
            if random.random() > 0.95:
                self.cpool_spare.remove(coord)
                self.cpool_zombie.append(coord)

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
            self.cgrid.put(
                drop=drop,
                rest=rest,
                s=c,
                cpair=cpair)
        for coord in self.cpool_zombie:
            (drop, rest) = coord
            (c, cpair) = PAIR_ZOMBIE
            self.cgrid.put(
                drop=drop,
                rest=rest,
                s=c,
                cpair=cpair)

def spin_simple_new(engine, height, width, cb_ready_alert, cb_grid_alert, cb_mail_alert, cb_over_alert):
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
        height=height,
        width=width,
        cb_ready_alert=cb_ready_alert,
        cb_grid_alert=cb_grid_alert,
        cb_mail_alert=cb_mail_alert,
        cb_over_alert=cb_over_alert)
    return ob

