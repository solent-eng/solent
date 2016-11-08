from solent.client.games.turnlib.fabric import fabric_new_grid # xxx !!! this goes
from solent.client.term.glyph import glyph_new

class RoguePlane(object):
    def __init__(self):
        # xxx !!! this goes
        self.fabric = fabric_new_grid()
        #
        self._glyphs = []
    def get_glyphs(self):
        return self._glyphs
    def create_glyph(self, s, e, c, cpair):
        glyph = glyph_new(
            s=s,
            e=e,
            c=c,
            cpair=cpair,
            rogue_plane=self)
        self._glyphs.append(glyph)
        return glyph
    def destroy_glyph(self, glyph):
        glyph.rogue_plane = None
        self._glyphs.remove(glyph)
    def move_nw(self, glyph):
        glyph.s += -1
        glyph.e += -1
    def move_nn(self, glyph):
        glyph.s += -1
        glyph.e += 0
    def move_ne(self, glyph):
        glyph.s += -1
        glyph.e += 1
    def move_ww(self, glyph):
        glyph.s += 0
        glyph.e += -1
    def move_ee(self, glyph):
        glyph.s += 0
        glyph.e += 1
    def move_sw(self, glyph):
        glyph.s += 1
        glyph.e += -1
    def move_ss(self, glyph):
        glyph.s += 1
        glyph.e += 0
    def move_se(self, glyph):
        glyph.s += 1
        glyph.e += 1

def rogue_plane_new():
    ob = RoguePlane()
    return ob

