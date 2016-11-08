class Meep(object):
    def __init__(self, s, e, c, cpair, rogue_plane):
        self.s = s
        self.e = e
        self.c = c
        self.cpair = cpair
        self.rogue_plane = rogue_plane

def meep_new(s, e, c, cpair, rogue_plane):
    ob = Meep(
        s=s,
        e=e,
        c=c,
        cpair=cpair,
        rogue_plane=rogue_plane)
    return ob

