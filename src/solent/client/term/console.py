#
# Bundle of stuff you need to put a terminal together. Typically, an
# application developer won't create these directly. Rather you'll call
# curses_term or window_term, and that will give you back an instance of this.
#

class Console(object):
    def __init__(self, keystream, grid_display):
        self.keystream = keystream
        self.grid_display = grid_display
    def screen_update(self, cgrid):
        self.grid_display.update(
            cgrid=cgrid)
    def getc(self):
        return self.keystream.getc()

def console_new(keystream, grid_display):
    ob = Console(
        keystream=keystream,
        grid_display=grid_display)
    return ob

