#
# console that follows roguelike conventions and can interact with a
# rogue_game.
#

from .logbook import logbook_new

from solent.client.constants import *
from solent.client.term.cgrid import cgrid_new
from solent.client.term.meep import meep_new
from solent.client.term.scope import scope_new
from solent.exceptions import SolentQuitException

from collections import deque

STATUS_NEW_CPAIR = SOL_CPAIR_YELLOW_T
STATUS_OLD_CPAIR = SOL_CPAIR_WHITE_T

class StatusEntry(object):
    def __init__(self, s):
        self.s = s
        #
        self.turns = 0

class RogueConsole(object):
    def __init__(self, rogue_game, cgrid, logbook):
        self.rogue_game = rogue_game
        self.cgrid = cgrid
        self.logbook = logbook
        #
        self.scope = scope_new(
            cursor_meep=rogue_game.player,
            margin_h=3,
            margin_w=5)
        #
        self.t = 0
        #
        self.status_entries = deque()
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
                self.cgrid.put(
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
    def redraw(self, grid_display):
        self.scope.populate_cgrid(
            cgrid=self.cgrid,
            meeps=self.rogue_game.get_meeps(),
            fabric=self.rogue_game.fabric)
        self._plot_status_messages()
        grid_display.update(
            cgrid=self.cgrid)
    def accept(self, key):
        fn = None
        #
        # direction processing
        movement = { 'q':   self.rogue_game.move_nw
                   , 'w':   self.rogue_game.move_nn
                   , 'e':   self.rogue_game.move_ne
                   , 'a':   self.rogue_game.move_ww
                   , 'd':   self.rogue_game.move_ee
                   , 'z':   self.rogue_game.move_sw
                   , 'x':   self.rogue_game.move_ss
                   , 'c':   self.rogue_game.move_se
                   }
        if key in movement:
            movement[key](
                meep=self.rogue_game.player)
            self.logbook.log(
                t=self.t,
                s='t %s: player moved to %ss%se'%(self.t, self.rogue_game.player.s, self.rogue_game.player.e))
            return

def rogue_console_new(rogue_game, width, height):
    cgrid = cgrid_new(
        width=width,
        height=height)
    logbook = logbook_new(
        capacity=100)
    ob = RogueConsole(
        rogue_game=rogue_game,
        cgrid=cgrid,
        logbook=logbook)
    return ob

