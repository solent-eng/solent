#
# experience: coordinates the menu for a game, and the entrypoint into a game.
#

from .fabric import fabric_new_grid
from .logbook import logbook_new

from solent.client.term.cgrid import cgrid_new
from solent.client.term.meep import meep_new
from solent.client.term.scope import scope_new

from solent.client.constants import *
from solent.exceptions import SolentQuitException

from collections import deque

STATUS_NEW_CPAIR = SOL_CPAIR_YELLOW_T
STATUS_OLD_CPAIR = SOL_CPAIR_WHITE_T

class StatusEntry(object):
    def __init__(self, s):
        self.s = s
        #
        self.turns = 0

class Game(object):
    def __init__(self, keystream, grid_display, cgrid, scope, logbook):
        self.keystream = keystream
        self.grid_display = grid_display
        self.cgrid = cgrid
        self.scope = scope
        self.logbook = logbook
        #
        self.t = 0
        #
        self.status_entries = deque()
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
        self._redraw_all()
        while True:
            self.t += 1
            self._player_turn()
            self._redraw_all()
    def _plot_status_messages(self):
        # filter new logbook entries into our local store
        for se in self.status_entries: se.turns += 1
        while self.status_entries and self.status_entries[-1].turns > 7:
            self.status_entries.pop()
        for s in self.logbook.recent():
            se = StatusEntry(s)
            self.status_entries.appendleft(se)
        # apply the local store to the grid
        for (idx, se) in enumerate(self.status_entries):
            if idx >= 7 and len(self.status_entries) >= 8:
                cgrid.put(
                    rest=0,
                    drop=idx,
                    s='..',
                    cpair=STATUS_OLD_CPAIR)
                break
            cpair = STATUS_NEW_CPAIR
            if se.turns > 0:
                cpair = STATUS_OLD_CPAIR
            self.cgrid.put(
                rest=0,
                drop=idx,
                s=se.s,
                cpair=cpair)
    def _redraw_all(self):
        self.scope.populate_cgrid(
            cgrid=self.cgrid,
            meeps=self.meeps,
            fabric=self.fabric)
        self._plot_status_messages()
        self.grid_display.update(
            cgrid=self.cgrid)
    def _player_turn(self):
        c = self.keystream.next()
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
            self.player.s += adjust_s
            self.player.e += adjust_e
            self.logbook.log(
                t=self.t,
                s='t %s: player moved to %ss%se'%(self.t, self.player.s, self.player.e))
            return

def game_new(term_shape, width, height):
    cgrid = cgrid_new(
        width=width,
        height=height)
    scope = scope_new(
        margin_h=3,
        margin_w=5)
    logbook = logbook_new(
        capacity=100)
    ob = Game(
        keystream=term_shape.get_keystream(),
        grid_display=term_shape.get_grid_display(),
        cgrid=cgrid,
        scope=scope,
        logbook=logbook)
    return ob

