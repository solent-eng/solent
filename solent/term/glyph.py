#
# glyph
#
# // overview
# Something that can live in a cell on a grid. It has south and east
# dimensions, a character and a colour pair.
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

class Glyph(object):
    def __init__(self, s, e, c, cpair):
        self.s = s
        self.e = e
        self.c = c # character
        self.cpair = cpair

def glyph_new(s, e, c, cpair):
    ob = Glyph(
        s=s,
        e=e,
        c=c,
        cpair=cpair)
    return ob

