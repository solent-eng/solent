#
# Bundle of stuff you need to put a terminal together. Typically, an
# application developer won't create these directly. Rather you'll call
# curses_term or window_term, and that will give you back an instance of this.
#

class TermShape(object):
    def __init__(self, keystream, grid_display):
        self.keystream = keystream
        self.grid_display = grid_display
    def get_grid_display(self):
        return self.grid_display
    def get_keystream(self):
        return self.keystream

def term_shape_new(keystream, grid_display):
    ob = TermShape(
        keystream=keystream,
        grid_display=grid_display)
    return ob

