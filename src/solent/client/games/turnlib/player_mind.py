#
# Mind is a standard concept in this system. Unlike most minds, the player
# mind doesn't serve as an AI. Rather, it's a mechanism through which the real
# player can interact with the system as though they are a mind. In this way,
# the player has no special treatment by the core game, they are just another
# participant.
#

from .mind import mind_interface

from collections import deque

class PlayerMind(object):
    def __init__(self, console, rogue_interaction):
        self.console = console
        self.rogue_interaction = rogue_interaction
        # keys that the user has sent into the system
        self.keys = deque()
        self.b_blocking = False
    def on_add_key(self, key):
        self.keys.append(key)
    def on_blocking_memo(self):
        self.b_blocking = True
    def on_turn(self, meep):
        self.b_blocking = False
        if not self.keys:
            return
        key = self.keys.popleft()
        plane_type = meep.plane.get_plane_type()
        if plane_type == 'RoguePlane':
            self.rogue_interaction.accept(
                meep=meep,
                key=key)
        else:
            raise Exception('unsupported plane_type [%s]'%plane_type)
    def on_ready(self):
        '''
        If there is no input queued, we return True to indicate that
        we are waiting for input (and therefore blocked).
        '''
        if self.keys:
            return True
        return False

def player_mind_new(console, rogue_interaction):
    inst = PlayerMind(
        console=console,
        rogue_interaction=rogue_interaction)
    w = mind_interface(
        cb_add_key=inst.on_add_key,
        cb_blocking_memo=inst.on_blocking_memo,
        cb_ready=inst.on_ready,
        cb_turn=inst.on_turn)
    return w

