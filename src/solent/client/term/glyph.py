#
# Glyph: Something that can live in a cell on a grid. It has south and east
# dimensions, a character and a colour pair.
#

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

