#
# Experience gives you a menu when you start the game. It displays a menu, and
# runs a demo game in the background.
#
# Experience is modal. In the default mode, we are interacting with the
# experience menu. At some point, the player will instruct to enter a game.
# Here, we get the keystrokes, and pass them through to a game object. If the
# player presses escape, then we come back to the menu.
#

from solent.client.constants import *
from solent.client.term.cgrid import cgrid_new
from solent.client.term.scope import scope_new
from solent.exceptions import SolentQuitException

CPAIR_MENU_BORDER = SOL_CPAIR_BLACK_CYAN
CPAIR_MENU_TEXT = SOL_CPAIR_T_WHITE
CPAIR_TITLE = SOL_CPAIR_T_WHITE

class Experience(object):
    def __init__(self, keystream, grid_display, cgrid, scope, title, menu):
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
        self.title = title
        self.menu = menu
        #
        self.title_cgrid = None
        self.__init_title()
        #
        self.menu_cgrid = None
        self.__init_menu()
    def __init_title(self):
        # Later on we could use something like pyfiglet for this. Better would
        # be a single distinct font, similar to what Gollop did with rebelstar.
        self.title_cgrid = cgrid_new(
            width=len(self.title),
            height=1)
        self.title_cgrid.put(
            drop=0,
            rest=0,
            s=self.title,
            cpair=CPAIR_TITLE)
    def __init_menu(self):
        lines = self.menu.get_lines()
        longest_line = 0
        for l in lines:
            longest_line = max( [longest_line, len(l)] )
        #
        # prepare the menu border
        self.menu_cgrid = cgrid_new(
            width=longest_line+4,
            height=len(lines)+4)
        horiz = ' '*(longest_line+4)
        blank = ' '*(longest_line+4)
        menu_border_height = len(lines)+2
        for idx in range(menu_border_height):
            if idx in (0, menu_border_height-1):
                self.menu_cgrid.put(
                    drop=idx,
                    rest=0,
                    s=horiz,
                    cpair=CPAIR_MENU_BORDER)
            else:
                line = lines[idx-1]
                self.menu_cgrid.put(
                    drop=idx,
                    rest=0,
                    s=' ',
                    cpair=CPAIR_MENU_BORDER)
                self.menu_cgrid.put(
                    drop=idx,
                    rest=1,
                    s=' %s%s '%(line, ' '*(longest_line-len(line))),
                    cpair=CPAIR_MENU_TEXT)
                self.menu_cgrid.put(
                    drop=idx,
                    rest=longest_line+3,
                    s=' ',
                    cpair=CPAIR_MENU_BORDER)
    def go(self):
        # draw instructions
        #
        self._redraw_all()
        while True:
            key = self.keystream.next()
            if self.menu.has_key(key):
                fn = self.menu.get_callback(key)
                fn()
            self._redraw_all()
    def _redraw_background_game(self):
        # xxx
        pass
    def _redraw_title(self):
        self.cgrid.blit(
            src_cgrid=self.title_cgrid,
            nail=(0, 0))
    def _redraw_menu(self):
        menu_drop = int( (self.cgrid.height / 2) - (self.menu_cgrid.height / 2) )
        menu_rest = int( (self.cgrid.width / 2) - (self.menu_cgrid.width / 2) )
        nail = (menu_drop, menu_rest)
        self.cgrid.blit(
            src_cgrid=self.menu_cgrid,
            nail=nail)
    def _redraw_all(self):
        self._redraw_background_game()
        self._redraw_title()
        self._redraw_menu()
        self.grid_display.update(
            cgrid=self.cgrid)

def experience_new(term_shape, width, height, title, menu):
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
        title=title,
        menu=menu)
    return ob

