#
# Glyph: Something that can live in a cell on a grid. It has south and east
# dimensions, a character and a colour pair.
#

class Glyph(object):
    def __init__(self, s, e, c, cpair, rogue_plane):
        self.s = s
        self.e = e
        self.c = c # character
        self.cpair = cpair
        self.rogue_plane = rogue_plane

def glyph_new(s, e, c, cpair, rogue_plane):
    ob = Glyph(
        s=s,
        e=e,
        c=c,
        cpair=cpair,
        rogue_plane=rogue_plane)
    return ob

