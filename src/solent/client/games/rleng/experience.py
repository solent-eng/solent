#
# Experience gives you a menu when you start the game. It displays a menu, and
# runs a demo game in the background.
#

from .menu import menu_new

from solent.client.term.cgrid import cgrid_new

class Experience(object):
    def __init__(self, keystream, grid_display, cgrid, menu):
        '''
        keystream: get this from a term_shape
        grid_display: get this from a term_shape
        cgrid: the memory to be used for rendering activity
        menu: instance of menu class that we display at startup
        '''
        self.keystream = keystream
        self.grid_display = grid_display
        self.cgrid = cgrid
        #
        # initial display
    def go(self):
        # draw instructions
        #
        self._redraw_all()
        while True:
            self.t += 1
            game_player_turn(self)
            self._redraw_all()
    def _redraw_menu(self):
        # xxx
        pass
    def _redraw_all(self):
        self._redraw_menu()
        self.scope.populate_cgrid(
            cgrid=self.cgrid,
            meeps=self.meeps,
            fabric=self.fabric,
            logbook=self.logbook)
        self.grid_display.update(
            cgrid=self.cgrid)

def experience_new(term_shape, width, height, menu):
    cgrid = cgrid_new(
        width=width,
        height=height)
    ob = Experience(
        keystream=term_shape.get_keystream(),
        grid_display=term_shape.get_grid_display(),
        cgrid=cgrid,
        menu=menu)
    return ob

