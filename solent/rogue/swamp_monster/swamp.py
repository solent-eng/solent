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

import random

class Swamp:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        #
        self.water_spots = []
        self.land_spots = []
        self.mangrove_spots = []
        #
        self._create_water()
        self._create_island()
        self._create_mangroves()
    def populate_chart(self, chart):
        for spot in self.water_spots:
            chart.put(spot, '~')
        for spot in self.land_spots:
            chart.put(spot, '.')
        for spot in self.mangrove_spots:
            chart.put(spot, '%')
    #
    def _create_water(self):
        for drop in range(self.height):
            for rest in range(self.width):
                self.water_spots.append( (drop, rest) )
    def _create_island(self):
        template = [ '~~??~???~~'
                   , '~????????~'
                   , '~???...???~'
                   , '???.....???'
                   , '???.....???'
                   , '???.....???'
                   , '????...????'
                   , '~?????????'
                   , '~~?~?~??~~'
                   ]
        #
        # Process the template into a sketch. This includes some basic
        # randomness.
        sketch = []
        for (ridx, row) in enumerate(template):
            sketch.append([])
            for (cidx, cell) in enumerate(row):
                if cell == '?':
                    cell = random.choice( ['~', '.'] )
                sketch[-1].append(cell)
        #
        drop_offset = int((self.height - len(sketch)) / 2)
        rest_offset = int((self.width - len(sketch[0])) / 2)
        for rest, row in enumerate(sketch):
            for drop, cell in enumerate(row):
                if cell == '.':
                    spot = (drop+drop_offset, rest+rest_offset)
                    self.water_spots.remove(spot)
                    self.land_spots.append(spot)
    def _create_mangroves(self):
        change = []
        for spot in self.water_spots:
            if random.random() > 0.9:
                change.append(spot)
        for spot in change:
            self.water_spots.remove(spot)
            self.mangrove_spots.append(spot)

def swamp_new(height, width):
    ob = Swamp(
        height=height,
        width=width)
    return ob

