#
# fabric: fabric is the surface/texture that entities sit on. you could think
# of it as being a bit like the concept of a level in other roguelikes.
#

from solent.client.constants import *

class GridFabric(object):
    def __init__(self):
        self.cross = ('+', SOL_CPAIR_BLUE_T)
        self.vert = ('-', SOL_CPAIR_BLUE_T)
        self.horiz = ('|', SOL_CPAIR_BLUE_T)
    def get_sigil(self, s, e):
        seven = (s%2 == 0)
        eeven = (e%2 == 0)
        if seven and eeven:
            return self.cross
        if seven:
            return self.vert
        if eeven:
            return self.horiz
        return None

class TerminalFabric(object):
    def __init__(self):
        self.dot = ('.', SOL_CPAIR_BLUE_T)
    def get_sigil(self, s, e):
        return self.dot

class DraughtsFabric(object):
    def __init__(self):
        pass
    def get_sigil(self, s, e):
        if s % 2 == 0 and e % 2 == 0:
            return ('.', SOL_CPAIR_BLUE_T)
        if s % 2 == 1 and e % 2 == 1:
            return ('.', SOL_CPAIR_BLUE_T)
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
            return ('-', SOL_CPAIR_GREEN_T)
        if s == 3 and e in (-2, 2):
            return ('|', SOL_CPAIR_GREEN_T)
        if se in ((2, -2), (4, 2)):
            return ('\\', SOL_CPAIR_GREEN_T)
        if se in ((4, -2), (2, 2)):
            return ('/', SOL_CPAIR_GREEN_T)
        #
        # dots around the entry box
        if se in ((1, -3), (5, -3), (1, 3), (5, 3)):
            return ('.', SOL_CPAIR_GREEN_T)
        #
        # don't draw bars at the entrypoint
        if 1 <= s <= 5 and e in (4, -4):
            return None
        #
        # mobius strip bars
        if se in ((0, -4), (0, 4), (6, -4), (6, 4)):
            return ('-', SOL_CPAIR_GREEN_T)
        #
        # texture dots
        #if s
        #
        # bars
        if (e-4) % 8 == 0:
            return ('|', SOL_CPAIR_GREEN_T)
        return None

def fabric_new_grid():
    ob = GridFabric()
    return ob

def fabric_new_terminal():
    ob = TerminalFabric()
    return ob

