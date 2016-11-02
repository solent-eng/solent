#
# Experience gives you a menu when you start the game. It displays a menu, and
# runs a demo game in the background.
#

from solent.client.constants import *
from solent.client.term.cgrid import cgrid_new
from solent.client.term.scope import scope_new
from solent.exceptions import SolentQuitException

CPAIR_MENU_BORDER = SOL_CPAIR_BLACK_CYAN
CPAIR_MENU_TEXT = SOL_CPAIR_T_WHITE

class Experience(object):
    def __init__(self, keystream, grid_display, cgrid, scope, menu):
        '''
        keystream: get this from a term_shape
        grid_display: get this from a term_shape
        cgrid: the memory to be used for rendering activity
        menu: instance of menu class that we display at startup
        '''
        self.keystream = keystream
        self.grid_display = grid_display
        self.cgrid = cgrid
        self.scope = scope
        self.menu = menu
        #
        # initialise the menu grid
        self.menu_border_cgrid = None;
        self.menu_content_cgrid = None
        self.__init_menu()
    def __init_menu(self):
        lines = self.menu.get_lines()
        longest_line = 0
        #
        # prepare the menu border
        self.menu_border_cgrid = cgrid_new(
            width=longest_line+4,
            height=len(lines)+4)
        horiz = '-'*longest_line
        blank = ' '*longest_line
        for idx, l in enumerate(lines):
            if idx in (0, len(lines)-1):
                self.menu_border_cgrid.put(
                    drop=idx,
                    rest=0,
                    s=horiz,
                    cpair=CPAIR_MENU_BORDER)
            else:
                self.menu_border_cgrid.put(
                    drop=idx,
                    rest=0,
                    s=blank,
                    cpair=CPAIR_MENU_BORDER)
        #
        # prepare the menu content
        for l in lines:
            longest_line = max( [longest_line, len(l)] )
        self.menu_content_cgrid = cgrid_new(
            width=longest_line,
            height=len(lines))
        for idx, l in enumerate(lines):
            self.menu_content_cgrid.put(
                drop=idx,
                rest=0,
                s=l,
                cpair=CPAIR_MENU_TEXT)
    def go(self):
        # draw instructions
        #
        self._redraw_all()
        while True:
            c = self.keystream.next()
            if 'Q' == c:
                raise SolentQuitException()
            self._redraw_all()
    def _redraw_background_game(self):
        # xxx
        pass
    def _redraw_menu(self):
        self.cgrid.blit(self.menu_border_cgrid)
        self.cgrid.blit(self.menu_content_cgrid)
    def _redraw_all(self):
        self._redraw_background_game()
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
    scope = scope_new(
        margin_h=3,
        margin_w=5)
    ob = Experience(
        keystream=term_shape.get_keystream(),
        grid_display=term_shape.get_grid_display(),
        cgrid=cgrid,
        scope=scope,
        menu=menu)
    return ob

