#
# Mind is a standard concept in this system. Unlike most minds, the player
# mind doesn't serve as an AI. Rather, it's a mechanism through which the real
# player can interact with the system as though they are a mind. In this way,
# the player has no special treatment by the core game, they are just another
# participant.
#

from collections import deque

ESC_KEY = 27

class PlayerMind(object):
    def __init__(self, console, menu_interaction, rogue_interaction):
        self.console = console
        self.menu_interaction = menu_interaction
        self.rogue_interaction = rogue_interaction
        # keys that the user has sent into the system
        self.keys = deque()
    def add_key(self, key):
        self.keys.append(key)
    def turn(self, meep):
        if not self.keys:
            return
        #
        # Input
        while self.keys:
            key = self.keys.popleft()
            if self.menu_interaction.active() and ord(key) == ESC_KEY:
                print('a')
                self.menu_interaction.set_active(False)
            elif not self.menu_interaction.active() and ord(key) == ESC_KEY:
                print('b')
                self.menu_interaction.set_active(True)
            elif self.menu_interaction.active():
                print('c')
                self.menu_interaction.accept(
                    key=key)
            else:
                plane_type = meep.plane.get_plane_type()
                if plane_type == 'RoguePlane':
                    self.rogue_interaction.accept(
                        meep=meep,
                        key=key)
                else:
                    raise Exception('unsupported plane_type [%s]'%plane_type)
        #
        # Output
        if self.menu_interaction.active():
            self.menu_interaction.redraw(
                console=self.console)
        else:
            plane_type = meep.plane.get_plane_type()
            if plane_type == 'RoguePlane':
                self.rogue_interaction.redraw(
                    console=self.console,
                    meep=meep)
            else:
                raise Exception('unsupported plane_type [%s]'%plane_type)
    def in_menu(self, key):
        self.menu_interaction.accept(
            key=key)

def player_mind_new(console, menu_interaction, rogue_interaction):
    ob = PlayerMind(
        console=console,
        menu_interaction=menu_interaction,
        rogue_interaction=rogue_interaction)
    return ob

