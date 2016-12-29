#
# rogue plane
#
# // work schedule
# xxx to glossary
# A plane is a dimension that (1) represents meeps and (2) has its own laws
# of physics. Examples:
#   *   Rogue plane: allows movement, fighting, getting/dropping of objects
#   *   Tactics plane allows selection and movement.
#   *   Editing plane might allow placement of text and scrolling.
#   *   Map plane might show continents divided into sectors (ala Risk) and
#       allow movement of tokens between neighbouring sectors.
#   *   Mobius plane might be similar to rogue plane, but have particular
#       wrapping laws.
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

from .meep import meep_new

from solent.console import e_colpair

import types

class RoguePlane(object):
    def __init__(self):
        self._terrain = []
        self._scrap = []
        self._meeps = []
    def get_plane_type(self):
        return 'RoguePlane'
    #
    # terrain: architecture of the plane
    def get_terrain(self):
        return self._terrain
    def create_terrain(self, s, e, c, cpair=e_colpair.purple_t):
        t = meep_new(
            mind=None,
            coords=rogue_plane_coords(
                s=s,
                e=e),
            c=c,
            cpair=cpair,
            plane=self)
        self._terrain.append(t)
    #
    # scrap: what you'd think of as inventory items. things that can be picked
    # up and operated on.
    def get_scrap(self):
        return self._scrap
    def create_scrap(self, s, e, c, cpair):
        scrap = meep_new(
            mind=None,
            coords=rogue_plane_coords(
                s=s,
                e=e),
            c=c,
            cpair=cpair,
            plane=self)
        self._scrap.append(scrap)
    #
    # meep: a mind's body on a plane
    def get_meeps(self):
        return self._meeps
    def create_meep(self, s, e, c, cpair, mind=None, overhead=10):
        meep = meep_new(
            overhead=overhead,
            mind=mind,
            coords=rogue_plane_coords(
                s=s,
                e=e),
            c=c,
            cpair=cpair,
            plane=self)
        self._meeps.append(meep)
        return meep
    def destroy_meep(self, meep):
        meep.plane = None
        self._meeps.remove(meep)
    #
    #
    def move_nw(self, meep):
        meep.coords.s += -1
        meep.coords.e += -1
    def move_nn(self, meep):
        meep.coords.s += -1
        meep.coords.e += 0
    def move_ne(self, meep):
        meep.coords.s += -1
        meep.coords.e += 1
    def move_ww(self, meep):
        meep.coords.s += 0
        meep.coords.e += -1
    def move_ee(self, meep):
        meep.coords.s += 0
        meep.coords.e += 1
    def move_sw(self, meep):
        meep.coords.s += 1
        meep.coords.e += -1
    def move_ss(self, meep):
        meep.coords.s += 1
        meep.coords.e += 0
    def move_se(self, meep):
        meep.coords.s += 1
        meep.coords.e += 1

def rogue_plane_new():
    ob = RoguePlane()
    return ob

def rogue_plane_coords(s, e):
    ob = types.ModuleType('rogue_plane_coords')
    ob.s = s
    ob.e = e
    return ob

