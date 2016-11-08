#
# scope: used to plot a grid around a glyph. The scope follows a glyph. It has
# some neat margin functionality in it. Rather than the glyph always being at
# the centre of the screen, the scope has margins. The scope only repoints
# when the glyph moves beyond the margins of the grid that's in focus.
#
# This is nice for the user, because the screen stays fairly consistent,
# rather than moving around all the time. It's also handy for rendering
# mechanisms such as ncurses, because it means there's less to update most of
# the time.
#

from solent.client.constants import *

class Scope(object):
    def __init__(self, perspective, margin_h, margin_w):
        self.margin_h = margin_h
        self.margin_w = margin_w
        self.perspective = perspective
        #
        self.adjust_h = 3
        self.adjust_w = 3
        self.centre_s = 0
        self.centre_e = 0
    def populate_cgrid(self, cgrid, fabric, glyphs):
        #
        # glyph preparation
        # -----------------
        #
        height = cgrid.height
        width = cgrid.width
        half_h = int(height / 2)
        half_w = int(width / 2)
        #
        # coords of the top left point we will render
        s_nail_s = self.centre_s - half_h
        s_nail_e = self.centre_e - half_w
        #
        # coords of the bottom right point we will render
        s_peri_s = s_nail_s + height
        s_peri_e = s_nail_e + width
        #
        # coords within the margin
        m_nail_s = s_nail_s + self.margin_h
        m_nail_e = s_nail_e + self.margin_w
        m_peri_s = s_peri_s - self.margin_h
        m_peri_e = s_peri_e - self.margin_w
        #
        # our focus point
        glyph_s = self.perspective.cursor.get_s()
        glyph_e = self.perspective.cursor.get_e()
        #
        # do we need to re-point the scope?
        # ---------------------------------
        # check to see that the glyph is within margins of the current scope.
        # If we need to adjust then re-point the scope, and then call this
        # function again.
        #
        adjust_s = 0
        adjust_e = 0
        if glyph_s < m_nail_s:
            adjust_s -= self.adjust_h
        if glyph_s >= m_peri_s:
            adjust_s += self.adjust_h
        if glyph_e < m_nail_e:
            adjust_e -= self.adjust_w
        if glyph_e >= m_peri_e:
            adjust_e += self.adjust_w
        #
        # do we need to repoint?
        if adjust_e or adjust_s:
            self.centre_s += adjust_s
            self.centre_e += adjust_e
            self.populate_cgrid(
                cgrid=cgrid,
                fabric=fabric,
                glyphs=glyphs)
            return
        #
        # display
        # -------
        #
        cgrid.clear()
        #
        # // fabric
        for (drop, south) in enumerate(range(s_nail_s, s_peri_s)):
            for (rest, east) in enumerate(range(s_nail_e, s_peri_e)):
                tpl = fabric.get_sigil(
                    s=south,
                    e=east)
                if None == tpl:
                    continue
                (c, cpair) = tpl
                cgrid.put(
                    rest=rest,
                    drop=drop,
                    s=c,
                    cpair=cpair)
        #
        # // glyphs
        for glyph in glyphs:
            if glyph.s < s_nail_s:
                continue
            if glyph.s >= s_peri_s:
                continue
            if glyph.e < s_nail_e:
                continue
            if glyph.e >= s_peri_e:
                continue
            cgrid.put(
                rest=glyph.e - s_nail_e,
                drop=glyph.s - s_nail_s,
                s=glyph.c,
                cpair=glyph.cpair)
        #
        # // ensure the cursor glyph is on top
        cursor_e = self.perspective.cursor.get_e()
        cursor_s = self.perspective.cursor.get_s()
        cursor_c = self.perspective.cursor.get_c()
        cursor_cpair = self.perspective.cursor.get_cpair()
        cgrid.put(
            rest=cursor_e - s_nail_e,
            drop=cursor_s - s_nail_s,
            s=cursor_c,
            cpair=cursor_cpair)

def scope_new(perspective, margin_h, margin_w):
    ob = Scope(
        perspective=perspective,
        margin_h=margin_h,
        margin_w=margin_w)
    return ob

