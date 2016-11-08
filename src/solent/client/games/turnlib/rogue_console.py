#
# console that follows roguelike conventions and can interact with a
# rogue_game.
#

from .logbook import logbook_new

from solent.client.constants import *
from solent.client.term.cgrid import cgrid_new
from solent.client.term.glyph import glyph_new
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
    def __init__(self, rogue_game, perspective, cgrid, logbook):
        self.rogue_game = rogue_game
        self.perspective = perspective
        self.cgrid = cgrid
        self.logbook = logbook
        #
        self.scope = scope_new(
            perspective=perspective,
            margin_h=3,
            margin_w=5)
        #
        self.t = 0
        #
        self.status_entries = deque()
    def _plot_status_messages(self):
        # filter new logbook entries into our local store
        for se in self.status_entries:
            se.turns += 1
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
        rogue_plane = self.rogue_game.player_meep.rogue_plane
        meeps = rogue_plane.get_meeps()
        #
        # /this seems inefficient, but at least it gives us a clean break
        # between meeps and glyphs.
        glyphs = []
        for meep in meeps:
            glyphs.append(
                glyph_new(
                    s=meep.s,
                    e=meep.e,
                    c=meep.c,
                    cpair=meep.cpair))
        #
        self.scope.populate_cgrid(
            cgrid=self.cgrid,
            glyphs=meeps)
        self._plot_status_messages()
        grid_display.update(
            cgrid=self.cgrid)
    def accept(self, key):
        fn = None
        #
        # direction processing
        rogue_plane = self.rogue_game.player_meep.rogue_plane
        movement = { 'q':   rogue_plane.move_nw
                   , 'w':   rogue_plane.move_nn
                   , 'e':   rogue_plane.move_ne
                   , 'a':   rogue_plane.move_ww
                   , 'd':   rogue_plane.move_ee
                   , 'z':   rogue_plane.move_sw
                   , 'x':   rogue_plane.move_ss
                   , 'c':   rogue_plane.move_se
                   }
        if key in movement:
            movement[key](
                meep=self.rogue_game.player_meep)
            self.logbook.log(
                t=self.t,
                s='t %s: player_meep moved to %ss%se'%(self.t, self.rogue_game.player_meep.s, self.rogue_game.player_meep.e))
            return

def rogue_console_new(rogue_game, perspective):
    cgrid = cgrid_new(
        width=perspective.width,
        height=perspective.height)
    logbook = logbook_new(
        capacity=100)
    ob = RogueConsole(
        rogue_game=rogue_game,
        perspective=perspective,
        cgrid=cgrid,
        logbook=logbook)
    return ob

