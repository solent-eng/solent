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

from solent.log import log

import random

class SwampGenerator:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        #
        self.water_spots = []
        self.land_spots = []
        #
        self._create_water()
        self._convert_some_water_to_land()
    def get_grid(self):
        '''
        Returns a 2d grid. Each cell will be either 'land' or 'water'.
        '''
        # create the grid
        grid = []
        for drop in range(self.height):
            grid.append([])
            for rest in range(self.width):
                grid[-1].append('void')
        #
        for (drop, rest) in self.water_spots:
            grid[drop][rest] = 'water'
        for (drop, rest) in self.land_spots:
            grid[drop][rest] = 'land'
        return grid
    #
    def _create_water(self):
        for drop in range(self.height):
            for rest in range(self.width):
                self.water_spots.append( (drop, rest) )
    def _convert_some_water_to_land(self):
        template = [ '~~???~???~~'
                   , '~~~?????~~~'
                   , '~???...???~'
                   , '~??.....??~'
                   , '???.....???'
                   , '~??.....??~'
                   , '~???...???~'
                   , '~~~?????~~~'
                   , '~~???~???~~'
                   ]
        #
        # Process the template into a sketch. This includes some basic
        # randomness.
        sketch = []
        for (ridx, row) in enumerate(template):
            sketch.append([])
            for (cidx, cell_c) in enumerate(row):
                if cell_c == '~':
                    cell_word = 'water'
                elif cell_c == '.':
                    cell_word = 'land'
                elif cell_c == '?':
                    cell_word = random.choice( ['water', 'land'] )
                else:
                    raise Exception('unhandled c [%s]'%cell_c)
                sketch[-1].append(cell_word)
        #
        drop_centre = int(self.height / 2)
        rest_centre = int(self.width / 2)
        sketch_height = len(sketch)
        sketch_width = len(sketch[0])
        drop_offset = drop_centre - int(sketch_height/2)
        rest_offset = rest_centre - int(sketch_width/2)
        for (drop, row) in enumerate(sketch):
            for (rest, cell) in enumerate(row):
                if cell == 'land':
                    spot = (drop+drop_offset, rest+rest_offset)
                    self.water_spots.remove(spot)
                    self.land_spots.append(spot)

def swamp_generator_new(height, width):
    ob = SwampGenerator(
        height=height,
        width=width)
    return ob

