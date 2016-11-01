#
# experience: coordinates the menu for a game, and the entrypoint into a game.
#

from .fabric import fabric_new_grid

from solent.client.term.cgrid import cgrid_new
from solent.client.term.logbook import logbook_new
from solent.client.term.meep import meep_new
from solent.client.term.scope import scope_new

from solent.client.constants import *
from solent.exceptions import SolentQuitException

def game_player_turn(game):
    c = game.keystream.next()
    if None == c:
        return
    if c == 'Q':
        raise SolentQuitException()
    #
    # direction processing
    b_move = False
    adjust_s = 0
    if c in 'qwe':
        b_move = True
        adjust_s -= 1
    if c in 'zxc':
        b_move = True
        adjust_s += 1
    adjust_e = 0
    if c in 'qaz':
        b_move = True
        adjust_e -= 1
    if c in 'edc':
        b_move = True
        adjust_e += 1
    if b_move:
        game.player.s += adjust_s
        game.player.e += adjust_e
        game.logbook.log(
            t=game.t,
            s='t %s: player moved to %ss%se'%(game.t, game.player.s, game.player.e))
        return

class Game(object):
    def __init__(self, keystream, grid_display, cgrid, logbook):
        self.keystream = keystream
        self.grid_display = grid_display
        self.cgrid = cgrid
        self.logbook = logbook
        #
        self.t = 0
        #
        self.scope = scope_new(
            margin_h=3,
            margin_w=5)
        #
        self.meeps = []
        self.meeps.append(
            meep_new(
                s=0,
                e=0,
                c='<',
                cpair=SOL_CPAIR_WHITE_T))
        self.meeps.append(
            meep_new(
                s=-2,
                e=-2,
                c='|',
                cpair=SOL_CPAIR_WHITE_T))
        self.meeps.append(
            meep_new(
                s=-3,
                e=0,
                c='|',
                cpair=SOL_CPAIR_WHITE_T))
        self.meeps.append(
            meep_new(
                s=-2,
                e=2,
                c='|',
                cpair=SOL_CPAIR_WHITE_T))
        self.meeps.append(
            meep_new(
                s=0,
                e=-3,
                c='|',
                cpair=SOL_CPAIR_WHITE_T))
        self.meeps.append(
            meep_new(
                s=0,
                e=3,
                c='|',
                cpair=SOL_CPAIR_WHITE_T))
        self.meeps.append(
            meep_new(
                s=2,
                e=-2,
                c='|',
                cpair=SOL_CPAIR_WHITE_T))
        self.meeps.append(
            meep_new(
                s=3,
                e=0,
                c='|',
                cpair=SOL_CPAIR_WHITE_T))
        self.meeps.append(
            meep_new(
                s=2,
                e=2,
                c='|',
                cpair=SOL_CPAIR_WHITE_T))
        #
        self.fabric = fabric_new_grid()
        self.player = meep_new(
            s=0,
            e=0,
            c='@',
            cpair=SOL_CPAIR_RED_T)
        self.meeps.append(self.player)
        self.scope.follow(self.player)
    def main_loop(self):
        self._redraw()
        while True:
            self.t += 1
            game_player_turn(self)
            self._redraw()
    def _redraw(self):
        self.scope.populate_cgrid(
            cgrid=self.cgrid,
            meeps=self.meeps,
            fabric=self.fabric,
            logbook=self.logbook)
        self.grid_display.update(
            cgrid=self.cgrid)

def game_new(term_shape, width, height):
    cgrid = cgrid_new(
        width=width,
        height=height)
    logbook = logbook_new(
        capacity=100)
    ob = Game(
        keystream=term_shape.get_keystream(),
        grid_display=term_shape.get_grid_display(),
        cgrid=cgrid,
        logbook=logbook)
    return ob

