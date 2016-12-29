#
# cell grid
#
# // overview
# This is a simple block of memory that holds display information. It has a
# width, and then a list of cells. Each cell consists of a character and a
# colour description.
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

from .enumerations import e_colpair

import sys
import types

DEFAULT_CPAIR = e_colpair.white_t

class Cell(object):
    def __init__(self):
        self.c = ' '
        self.cpair = DEFAULT_CPAIR
    def compare(self, spot):
        if self.c != spot.c:
            return False
        if self.cpair != spot.cpair:
            return False
        return True
    def mimic(self, spot):
        self.c = spot.c
        self.cpair = spot.cpair
    def __repr__(self):
        return 'cell[%s/%s]'%(self.c, self.cpair)

class CellGrid(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        #
        self.spots = []
        #
        self.set_dimensions(
            width=width,
            height=height)
    def set_dimensions(self, width, height):
        self.spots = []
        for idx in range(width*height):
            self.spots.append(Cell())
    def clear(self):
        for spot in self.spots:
            spot.c = ' '
            spot.cpair = DEFAULT_CPAIR
    def get(self, drop, rest):
        return self.spots[ (drop*self.width) + rest ]
    def put(self, drop, rest, s, cpair):
        if type(s) != str:
            s = str(s)
        offset = int((int(drop)*self.width) + int(rest))
        for idx, c in enumerate(s):
            spot = self.spots[offset+idx]
            spot.c = c
            spot.cpair = cpair
    def _put_spots(self, drop, rest, spots):
        offset = (drop*self.width) + rest
        for idx, src_spot in enumerate(spots):
            spot = self.spots[offset+idx]
            spot.mimic(src_spot)
    def blit(self, src_cgrid, nail=None, peri=None):
        '''copies the supplied cgrid onto your grid, starting at the coords
        a, and ending at coords b. Coords should be in format (drop, rest).
        If coords_a is None, it starts at (0,0). If coords_b is None, then
        it goes as fills in as much of the space that's available with as
        much of the content that's available.

        * nail: d/r coords on the destination cgrid where the copy starts
        
        * peri: d/r coords marking the termination of the copy (i.e. the
          beyond is one unit further south and one unit further east of the
          final position to be copied).
        '''
        if None == nail:
            nail = (0, 0)
        (nail_drop, nail_rest) = nail
        if nail_drop >= self.height or nail_rest >= self.width:
            return
        #
        # Explaining the min below: consider if the caller was trying to
        # copy a src_grid which overshot the sides of the source array.
        # Here we guard against that.
        if None == peri:
            peri = (self.height, self.width)
        peri_drop = min( [peri[0], self.height, (nail_drop+src_cgrid.height)] )
        peri_rest = min( [peri[1], self.width, (nail_rest+src_cgrid.width)] )
        #
        segment_width = peri_rest - nail_rest
        for idx in range(peri_drop-nail_drop):
            # We're copying rows at a time here. First trick is to work out
            # what the segments are of the source-grid spots array, and our
            # dest-grid spots array.
            src_spots_nail = (idx * src_cgrid.width)
            src_spots_peri = src_spots_nail + segment_width
            src_spots = src_cgrid.spots[src_spots_nail:src_spots_peri]
            #
            dst_drop = nail_drop + idx
            dst_rest = nail_rest
            self._put_spots(
                drop=dst_drop,
                rest=dst_rest,
                spots=src_spots)

def cgrid_new(width, height):
    ob = CellGrid(
        width=width,
        height=height)
    return ob

