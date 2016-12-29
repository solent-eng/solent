#
# rogue_interaction
#
# // overview
# This translates a player's keystrokes into interactions with a rogue_plane.
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

from .logbook import logbook_new

from solent.console import e_colpair
from solent.console import cgrid_new
from solent.console import glyph_new
from solent.console import scope_new
from solent.exceptions import SolentQuitException

from collections import deque

STATUS_NEW_CPAIR = e_colpair.yellow_t
STATUS_OLD_CPAIR = e_colpair.white_t

class StatusEntry(object):
    def __init__(self, s):
        self.s = s
        #
        self.turns = 0

class RogueInteraction(object):
    def __init__(self, console, cursor, cgrid, logbook):
        self.console = console
        self.cursor = cursor
        self.cgrid = cgrid
        self.logbook = logbook
        #
        self.scope = scope_new(
            cursor=cursor,
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
    def render(self, rogue_plane):
        # xxx refactor to field-of-view
        #
        # /this seems inefficient, but at least it gives us a clean break
        # between meeps and glyphs.
        glyphs = []
        def add_glyph(s, e, c, cpair):
            g = glyph_new(
                s=s,
                e=e,
                c=c,
                cpair=cpair)
            glyphs.append(g)
        for terrain in rogue_plane.get_terrain():
            add_glyph(
                s=terrain.coords.s,
                e=terrain.coords.e,
                c=terrain.c,
                cpair=terrain.cpair)
        for scrap in rogue_plane.get_scrap():
            add_glyph(
                s=scrap.coords.s,
                e=scrap.coords.e,
                c=scrap.c,
                cpair=scrap.cpair)
        for meep in rogue_plane.get_meeps():
            add_glyph(
                s=meep.coords.s,
                e=meep.coords.e,
                c=meep.c,
                cpair=meep.cpair)
        #
        self.scope.populate_cgrid(
            cgrid=self.cgrid,
            glyphs=glyphs)
        self._plot_status_messages()
        self.console.screen_update(
            cgrid=self.cgrid)
    def accept(self, meep, key):
        fn = None
        #
        # direction processing
        rogue_plane = meep.plane
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
                meep=meep)
            return

def rogue_interaction_new(console, cursor):
    cgrid = cgrid_new(
        width=console.width,
        height=console.height)
    logbook = logbook_new(
        capacity=100)
    ob = RogueInteraction(
        console=console,
        cursor=cursor,
        cgrid=cgrid,
        logbook=logbook)
    return ob

