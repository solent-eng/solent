class Perspective(object):
    def __init__(self, cursor, width, height):
        self.cursor = cursor
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

def perspective_new(cursor, width, height):
    ob = Perspective(
        cursor=cursor,
        width=width,
        height=height)
    return ob

