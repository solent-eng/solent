#
# algobunny_mind
#
# // license
# Copyright 2016, Free Software Foundation.
#
# This file is part of Solent.
#
# Solent is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# Solent is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# Solent. If not, see <http://www.gnu.org/licenses/>.
# .

from .mind import mind_interface

class AlgobunnyMind(object):
    def __init__(self):
        self.mode = 0
        self.counter = 4
    def on_add_key(self, key):
        pass
    def on_blocking_memo(self):
        pass
    def on_is_blocking(self):
        return False
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
    inst = AlgobunnyMind()
    i = mind_interface(
        cb_add_key=inst.on_add_key,
        cb_blocking_memo=inst.on_blocking_memo,
        cb_is_blocking=inst.on_is_blocking,
        cb_ready=inst.on_ready,
        cb_turn=inst.on_turn)
    return i

