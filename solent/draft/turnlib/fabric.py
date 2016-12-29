#
# fabric
#
# // overview
# fabric is the surface/texture that entities sit on. you could think of it as
# being a bit like the concept of a level in other roguelikes.
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

from solent.console import e_colpair

class GridFabric(object):
    def __init__(self):
        self.cross = ('+', e_colpair.blue_t)
        self.horiz = ('-', e_colpair.blue_t)
        self.vert = ('|', e_colpair.blue_t)
    def get_sigil(self, s, e):
        seven = (s%8 == 0)
        eeven = (e%8 == 0)
        if seven and eeven:
            return self.cross
        if seven:
            return self.horiz
        if eeven:
            return self.vert
        return None

class TerminalFabric(object):
    def __init__(self):
        self.dot = ('.', e_colpair.blue_t)
    def get_sigil(self, s, e):
        return self.dot

class DraughtsFabric(object):
    def __init__(self):
        pass
    def get_sigil(self, s, e):
        if s % 2 == 0 and e % 2 == 0:
            return ('.', e_colpair.blue_t)
        if s % 2 == 1 and e % 2 == 1:
            return ('.', e_colpair.blue_t)
        return None

class GreenFabric(object):
    '''
    Intended fabric for presenting memory. Haven't yet worked out how
    navitagion will work. Want it to function as a mobius strip. Perhaps my
    notions of south and east are misplaced.

    Current thought is to steer it towards this kind of display:

        #            
        #   56704   8       1028
        #                    
        #                    
        #                    
        #   56700   0       1024
        #            \-/ n   
        #            | |     
        #            /-\ (   
        #   56694   60424   1020
        #

    Considered using the 0 as the portal. But this complicates writing to the
    zero sector. Better to have a utility space, as here.
    The starting O is the portal

    Unsure how to model a mobius strip. There might be people who have advice
    on this online. Or in the roguelike forums even. srd may have ideas as
    well. Or look at his code.
    '''
    def __init__(self):
        pass
    def get_sigil(self, s, e):
        se = (s, e)
        #
        # entry box
        if s in (2, 4) and -1 <= e <= 1:
            return ('-', e_colpair.green_t)
        if s == 3 and e in (-2, 2):
            return ('|', e_colpair.green_t)
        if se in ((2, -2), (4, 2)):
            return ('\\', e_colpair.green_t)
        if se in ((4, -2), (2, 2)):
            return ('/', e_colpair.green_t)
        #
        # dots around the entry box
        if se in ((1, -3), (5, -3), (1, 3), (5, 3)):
            return ('.', e_colpair.green_t)
        #
        # don't draw bars at the entrypoint
        if 1 <= s <= 5 and e in (4, -4):
            return None
        #
        # mobius strip bars
        if se in ((0, -4), (0, 4), (6, -4), (6, 4)):
            return ('-', e_colpair.green_t)
        #
        # texture dots
        #if s
        #
        # bars
        if (e-4) % 8 == 0:
            return ('|', e_colpair.green_t)
        return None

def fabric_new_grid():
    ob = GridFabric()
    return ob

def fabric_new_terminal():
    ob = TerminalFabric()
    return ob

