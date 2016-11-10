#
# Mind is a standard concept in this system. Unlike most minds, the player
# mind doesn't serve as an AI. Rather, it's a mechanism through which the real
# player can interact with the system as though they are a mind. In this way,
# the player has no special treatment by the core game, they are just another
# participant.
#

from collections import deque

class PlayerMind(object):
    def __init__(self, console):
        self.console = console
        # keys that the user has sent into the system
        self.keys = deque()
    def add_key(self, key):
        if key in (None, ''):
            return
        self.keys.append(key)
    def turn(self, meep):
        if not self.keys:
            self.console.redraw(
                plane=meep.plane,
                grid_display=self.grid_display)
        # xxx what happens here? major refactor I suspect
        self.console.accept(
            plane=meep.plane,
            key=key)
        self.console.redraw(
            plane=meep.plane,
            grid_display=self.grid_display)

def player_mind_new(console):
    ob = PlayerMind(
        console=console)
    return ob

