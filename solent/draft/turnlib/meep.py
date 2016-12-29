#
# meep
#
# // overview
# Think or it as an entity in Entity-Component model speak
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
# .

from solent.console import e_colpair

DEFAULT_CPAIR = e_colpair.t_red

class Meep(object):
    def __init__(self, overhead, mind, plane, coords, c, cpair):
        self.mind = mind
        self.coords = coords
        self.c = c
        self.cpair = cpair
        self.plane = plane
        self.overhead = overhead
        #
        # creation has inherent fatigue
        self.fatigue = overhead
        #
        # mind should set this
        self.has_died = False

def meep_new(overhead=10, mind=None, plane=None, coords=None, c='x', cpair=DEFAULT_CPAIR):
    ob = Meep(
        mind=mind,
        plane=plane,
        coords=coords,
        c=c,
        cpair=cpair,
        overhead=overhead)
    return ob

