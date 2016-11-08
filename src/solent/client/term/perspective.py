class Perspective(object):
    def __init__(self, cursor_glyph, width, height):
        self.cursor_glyph = cursor_glyph
        self.width = width
        self.height = height
        #
        self.tiles = []
        self.scrap = []
        self.glyphs = []
    def clear(self):
        self.tiles = []
        self.scrap = []
        self.glyphs = []

def perspective_new(cursor_glyph, width, height):
    ob = Perspective(
        cursor_glyph=cursor_glyph,
        width=width,
        height=height)
    return ob

