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


# --------------------------------------------------------
#   :testing
# --------------------------------------------------------
def cgrid_console_print(cgrid):
    for h in range(cgrid.height):
        nail = (h*cgrid.width)
        peri = nail + cgrid.width
        spots = cgrid.spots[nail:peri]
        line = ''.join( [s.c for s in spots] )
        print('%2s|%s'%(h, line))

def cgrid_populate(cgrid, c):
    for drop in range(cgrid.height):
        cgrid.put(
            drop=drop,
            rest=0,
            s=c*cgrid.height,
            cpair=DEFAULT_CPAIR)

TESTS = []
def test(fn):
    global TESTS
    def go():
        print('// --------------------------------------------------------')
        print('//  %s'%fn.__name__)
        print('// --------------------------------------------------------')
        fn()
        print('')
    TESTS.append(go)
    return go

def run_tests():
    global TESTS
    for t in TESTS:
        t()

@test
def test_a():
    print('//two simple grids')
    grid_a = cgrid_new(5, 5)
    cgrid_populate(grid_a, '-')
    cgrid_console_print(grid_a)
    #
    grid_b = cgrid_new(3, 3)
    cgrid_populate(grid_b, '|')
    cgrid_console_print(grid_b)

@test
def test_b():
    print('//grid_b onto grid_a')
    grid_a = cgrid_new(5, 5)
    cgrid_populate(grid_a, '*')
    #
    grid_b = cgrid_new(3, 3)
    grid_b.put(0, 0, 'a', DEFAULT_CPAIR)
    grid_b.put(0, 1, 'b', DEFAULT_CPAIR)
    grid_b.put(0, 2, 'c', DEFAULT_CPAIR)
    grid_b.put(1, 0, 'd', DEFAULT_CPAIR)
    grid_b.put(1, 1, 'e', DEFAULT_CPAIR)
    grid_b.put(1, 2, 'f', DEFAULT_CPAIR)
    grid_b.put(2, 0, 'g', DEFAULT_CPAIR)
    grid_b.put(2, 1, 'h', DEFAULT_CPAIR)
    grid_b.put(2, 2, 'i', DEFAULT_CPAIR)
    #
    grid_a.blit(grid_b)
    cgrid_console_print(grid_a)

@test
def test_c():
    print('//truncated copy right')
    grid_a = cgrid_new(5, 5)
    zyx = [chr(i+65) for i in range(26)]
    zyx.reverse()
    for i in range(25):
        l = zyx[i]
        drop = i / 5
        rest = i % 5
        grid_a.put(
            drop=drop,
            rest=rest,
            s=l.lower(),
            cpair=DEFAULT_CPAIR)
    #
    grid_b = cgrid_new(3, 3)
    grid_b.put(0, 0, '0', DEFAULT_CPAIR)
    grid_b.put(0, 1, '1', DEFAULT_CPAIR)
    grid_b.put(0, 2, '2', DEFAULT_CPAIR)
    grid_b.put(1, 0, '3', DEFAULT_CPAIR)
    grid_b.put(1, 1, '4', DEFAULT_CPAIR)
    grid_b.put(1, 2, '5', DEFAULT_CPAIR)
    grid_b.put(2, 0, '6', DEFAULT_CPAIR)
    grid_b.put(2, 1, '7', DEFAULT_CPAIR)
    grid_b.put(2, 2, '8', DEFAULT_CPAIR)
    #
    grid_a.blit(
        src_cgrid=grid_b,
        nail=(1,3))
    cgrid_console_print(grid_a)

@test
def test_d():
    print('//truncated copy bottom')
    grid_a = cgrid_new(5, 5)
    zyx = [chr(i+65) for i in range(26)]
    zyx.reverse()
    for i in range(25):
        l = zyx[i]
        drop = i / 5
        rest = i % 5
        grid_a.put(
            drop=drop,
            rest=rest,
            s=l.lower(),
            cpair=DEFAULT_CPAIR)
    #
    grid_b = cgrid_new(3, 3)
    grid_b.put(0, 0, '0', DEFAULT_CPAIR)
    grid_b.put(0, 1, '1', DEFAULT_CPAIR)
    grid_b.put(0, 2, '2', DEFAULT_CPAIR)
    grid_b.put(1, 0, '3', DEFAULT_CPAIR)
    grid_b.put(1, 1, '4', DEFAULT_CPAIR)
    grid_b.put(1, 2, '5', DEFAULT_CPAIR)
    grid_b.put(2, 0, '6', DEFAULT_CPAIR)
    grid_b.put(2, 1, '7', DEFAULT_CPAIR)
    grid_b.put(2, 2, '8', DEFAULT_CPAIR)
    #
    grid_a.blit(
        src_cgrid=grid_b,
        nail=(3,1))
    cgrid_console_print(grid_a)

@test
def test_e():
    print('//no nail')
    grid_a = cgrid_new(5, 5)
    zyx = [chr(i+65) for i in range(26)]
    zyx.reverse()
    for i in range(25):
        l = zyx[i]
        drop = i / 5
        rest = i % 5
        grid_a.put(
            drop=drop,
            rest=rest,
            s=l.lower(),
            cpair=DEFAULT_CPAIR)
    #
    grid_b = cgrid_new(3, 3)
    grid_b.put(0, 0, '0', DEFAULT_CPAIR)
    grid_b.put(0, 1, '1', DEFAULT_CPAIR)
    grid_b.put(0, 2, '2', DEFAULT_CPAIR)
    grid_b.put(1, 0, '3', DEFAULT_CPAIR)
    grid_b.put(1, 1, '4', DEFAULT_CPAIR)
    grid_b.put(1, 2, '5', DEFAULT_CPAIR)
    grid_b.put(2, 0, '6', DEFAULT_CPAIR)
    grid_b.put(2, 1, '7', DEFAULT_CPAIR)
    grid_b.put(2, 2, '8', DEFAULT_CPAIR)
    #
    grid_a.blit(
        src_cgrid=grid_b)
    cgrid_console_print(grid_a)

if __name__ == '__main__':
    run_tests()



