#
# Cell Grid. This is a simple block of memory that holds display information.
# It has a width, and then a list of cells. Each cell consists of a
# character and a colour description.
#

from solent.client.constants import *

DEFAULT_CPAIR = SOL_CPAIR_WHITE_T

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
    def put(self, drop, rest, s, cpair):
        offset = (drop*self.width) + rest
        for idx, c in enumerate(s):
            spot = self.spots[offset+idx]
            spot.c = c
            spot.cpair = cpair

def cgrid_new(width, height):
    ob = CellGrid(
        width=width,
        height=height)
    return ob

