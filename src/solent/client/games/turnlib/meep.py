class Meep(object):
    def __init__(self, mind, s, e, c, cpair, rogue_plane, overhead):
        self.mind = mind
        self.s = s
        self.e = e
        self.c = c
        self.cpair = cpair
        self.rogue_plane = rogue_plane
        self.overhead = overhead
        #
        # creation has inherent fatigue
        self.fatigue = overhead
        #
        # mind should set this
        self.has_died = False

def meep_new(mind, s, e, c, cpair, rogue_plane, overhead=10):
    ob = Meep(
        mind=mind,
        s=s,
        e=e,
        c=c,
        cpair=cpair,
        rogue_plane=rogue_plane,
        overhead=overhead)
    return ob

