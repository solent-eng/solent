from solent.client.constants import SOL_CPAIR_T_RED

DEFAULT_CPAIR = SOL_CPAIR_T_RED

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

