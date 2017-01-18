#
# meep
#
# // overview
# The game map consists of two types of things. There are tiles. These are the
# surface of the game. And then there are meeps. These are things that can be
# interacted with on the map. No doubt at some future time there will be
# something that represents scrap.
#
# This structure describes a meeps: things that can be interacted with on the
# map.
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

class Meep:
    def __init__(self, h, drop, rest, sigil_h, b_is_player):
        self.h = h
        self.drop = drop
        self.rest = rest
        self.sigil_h = sigil_h
        self.b_is_player = b_is_player
    def spot(self):
        return (self.drop, self.rest)

def meep_new(h, drop, rest, sigil_h, b_is_player):
    ob = Meep(
        h=h,
        drop=drop,
        rest=rest,
        sigil_h=sigil_h,
        b_is_player=b_is_player)
    return ob

