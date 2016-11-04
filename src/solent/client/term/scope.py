#
# scope: used to plot a grid around a meep. The scope follows a meep. It has
# some neat margin functionality in it. Rather than the meep always being at
# the centre of the screen, the scope has margins. The scope only repoints
# when the meep moves beyond the margins of the grid that's in focus.
#
# This is nice for the user, because the screen stays fairly consistent,
# rather than moving around all the time. It's also handy for rendering
# mechanisms such as ncurses, because it means there's less to update most of
# the time.
#

from solent.client.constants import *

class Scope(object):
    def __init__(self, meep, margin_h, margin_w):
        self.meep = meep
        self.margin_h = margin_h
        self.margin_w = margin_w
        #
        self.adjust_h = 3
        self.adjust_w = 3
        self.centre_s = 0
        self.centre_e = 0
    def populate_cgrid(self, cgrid, fabric, meeps):
        if None == self.meep:
            raise Exception("need to follow a meep")
        #
        # meep preparation
        # ----------------
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
        meep_s = self.meep.s
        meep_e = self.meep.e
        #
        # do we need to re-point the scope?
        # ---------------------------------
        # check to see that the meep is within margins of the current scope.
        # If we need to adjust then re-point the scope, and then call this
        # function again.
        #
        adjust_s = 0
        adjust_e = 0
        if meep_s < m_nail_s:
            adjust_s -= self.adjust_h
        if meep_s >= m_peri_s:
            adjust_s += self.adjust_h
        if meep_e < m_nail_e:
            adjust_e -= self.adjust_w
        if meep_e >= m_peri_e:
            adjust_e += self.adjust_w
        #
        # do we need to repoint?
        if adjust_e or adjust_s:
            self.centre_s += adjust_s
            self.centre_e += adjust_e
            self.populate_cgrid(
                cgrid=cgrid,
                fabric=fabric,
                meeps=meeps)
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
        # // meeps
        for meep in meeps:
            if meep.s < s_nail_s:
                continue
            if meep.s >= s_peri_s:
                continue
            if meep.e < s_nail_e:
                continue
            if meep.e >= s_peri_e:
                continue
            cgrid.put(
                rest=meep.e - s_nail_e,
                drop=meep.s - s_nail_s,
                s=meep.c,
                cpair=meep.cpair)

def scope_new(meep, margin_h, margin_w):
    ob = Scope(
        meep=meep,
        margin_h=margin_h,
        margin_w=margin_w)
    return ob

