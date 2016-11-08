from .meep import meep_new

class RoguePlane(object):
    def __init__(self):
        self._meeps = []
    def get_meeps(self):
        return self._meeps
    def create_meep(self, s, e, c, cpair):
        meep = meep_new(
            s=s,
            e=e,
            c=c,
            cpair=cpair,
            rogue_plane=self)
        self._meeps.append(meep)
        return meep
    def destroy_meep(self, meep):
        meep.rogue_plane = None
        self._meeps.remove(meep)
    def move_nw(self, meep):
        meep.s += -1
        meep.e += -1
    def move_nn(self, meep):
        meep.s += -1
        meep.e += 0
    def move_ne(self, meep):
        meep.s += -1
        meep.e += 1
    def move_ww(self, meep):
        meep.s += 0
        meep.e += -1
    def move_ee(self, meep):
        meep.s += 0
        meep.e += 1
    def move_sw(self, meep):
        meep.s += 1
        meep.e += -1
    def move_ss(self, meep):
        meep.s += 1
        meep.e += 0
    def move_se(self, meep):
        meep.s += 1
        meep.e += 1

def rogue_plane_new():
    ob = RoguePlane()
    return ob

