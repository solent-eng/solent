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

from collections import deque

STATUS_NEW_CPAIR = SOL_CPAIR_YELLOW_T
STATUS_OLD_CPAIR = SOL_CPAIR_WHITE_T

class StatusEntry(object):
    def __init__(self, s):
        self.s = s
        #
        self.turns = 0

class Scope(object):
    def __init__(self, margin_h, margin_w):
        self.margin_h = margin_h
        self.margin_w = margin_w
        #
        self.meep = None
        self.status_entries = deque()
        self.adjust_h = 3
        self.adjust_w = 3
        self.centre_s = 0
        self.centre_e = 0
        self.log = deque()
    def follow(self, meep):
        self.meep = meep
    def populate_cgrid(self, cgrid, fabric, meeps, logbook):
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
        s_beyond_s = s_nail_s + height
        s_beyond_e = s_nail_e + width
        #
        # coords within the margin
        m_nail_s = s_nail_s + self.margin_h
        m_nail_e = s_nail_e + self.margin_w
        m_beyond_s = s_beyond_s - self.margin_h
        m_beyond_e = s_beyond_e - self.margin_w
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
        if meep_s >= m_beyond_s:
            adjust_s += self.adjust_h
        if meep_e < m_nail_e:
            adjust_e -= self.adjust_w
        if meep_e >= m_beyond_e:
            adjust_e += self.adjust_w
        #
        # do we need to repoint?
        if adjust_e or adjust_s:
            self.centre_s += adjust_s
            self.centre_e += adjust_e
            self.populate_cgrid(
                cgrid=cgrid,
                fabric=fabric,
                meeps=meeps,
                logbook=logbook)
            return
        #
        # status preparation
        # ------------------
        #
        for se in self.status_entries: se.turns += 1
        while self.status_entries and self.status_entries[-1].turns > 7:
            self.status_entries.pop()
        for s in logbook.recent():
            se = StatusEntry(s)
            self.status_entries.appendleft(se)
        #
        # display
        # -------
        #
        cgrid.clear()
        #
        # // fabric
        for (drop, south) in enumerate(range(s_nail_s, s_beyond_s)):
            for (rest, east) in enumerate(range(s_nail_e, s_beyond_e)):
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
            if meep.s >= s_beyond_s:
                continue
            if meep.e < s_nail_e:
                continue
            if meep.e >= s_beyond_e:
                continue
            cgrid.put(
                rest=meep.e - s_nail_e,
                drop=meep.s - s_nail_s,
                s=meep.c,
                cpair=meep.cpair)
        #
        # // status messages
        for (idx, se) in enumerate(self.status_entries):
            if idx >= 7 and len(self.status_entries) >= 8:
                cgrid.put(
                    rest=0,
                    drop=idx,
                    s='..',
                    cpair=STATUS_OLD_CPAIR)
                break
            cpair = STATUS_NEW_CPAIR
            if se.turns > 0:
                cpair = STATUS_OLD_CPAIR
            cgrid.put(
                rest=0,
                drop=idx,
                s=se.s,
                cpair=cpair)

def scope_new(margin_h, margin_w):
    ob = Scope(
        margin_h=margin_h,
        margin_w=margin_w)
    return ob

