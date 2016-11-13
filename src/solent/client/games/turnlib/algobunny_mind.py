from .mind import mind_interface

class AlgobunnyMind(object):
    def __init__(self):
        self.mode = 0
        self.counter = 4
    def on_add_key(self, key):
        pass
    def on_blocking_memo(self):
        pass
    def on_ready(self):
        return True
    def on_turn(self, meep):
        plane = meep.plane
        plane_type = plane.get_plane_type()
        if plane_type == 'RoguePlane':
            if self.mode == 0:
                plane.move_ee(
                    meep=meep)
            elif self.mode == 1:
                plane.move_ss(
                    meep=meep)
            elif self.mode == 2:
                plane.move_ww(
                    meep=meep)
            elif self.mode == 3:
                plane.move_nn(
                    meep=meep)
            else:
                raise Exception('invalid mode [%s]'%self.mode)
        else:
            raise Exception('unsupported plane_type [%s]'%plane_type)
        #
        # Change internal state so that it will be ready for next move
        if self.counter == 0:
            self.mode += 1
            if 4 == self.mode:
                self.mode = 0
            self.counter = 4
        else:
            self.counter -= 1

def algobunny_mind_new():
    impl = AlgobunnyMind()
    i = mind_interface(
        cb_add_key=impl.on_add_key,
        cb_blocking_memo=impl.on_blocking_memo,
        cb_ready=impl.on_ready,
        cb_turn=impl.on_turn)
    return i

