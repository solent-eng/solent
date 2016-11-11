#
# Mind is a standard concept in this system. Unlike most minds, the player
# mind doesn't serve as an AI. Rather, it's a mechanism through which the real
# player can interact with the system as though they are a mind. In this way,
# the player has no special treatment by the core game, they are just another
# participant.
#

from collections import deque

class PlayerMind(object):
    def __init__(self, console, rogue_interaction):
        self.console = console
        self.rogue_interaction = rogue_interaction
        # keys that the user has sent into the system
        self.keys = deque()
    def add_key(self, key):
        self.keys.append(key)
    def turn(self, meep):
        #
        # Input
        while self.keys:
            key = self.keys.popleft()
            plane_type = meep.plane.get_plane_type()
            if plane_type == 'RoguePlane':
                self.rogue_interaction.accept(
                    meep=meep,
                    key=key)
            else:
                raise Exception('unsupported plane_type [%s]'%plane_type)
        #
        # Output
        plane_type = meep.plane.get_plane_type()
        if plane_type == 'RoguePlane':
            self.rogue_interaction.render(
                meep=meep)
        else:
            raise Exception('unsupported plane_type [%s]'%plane_type)
    def in_menu(self, key):
        self.control_menu.accept(
            key=key)

def player_mind_new(console, rogue_interaction):
    ob = PlayerMind(
        console=console,
        rogue_interaction=rogue_interaction)
    return ob

