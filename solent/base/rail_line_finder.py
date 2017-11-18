# // license
# Copyright 2016, Free Software Foundation.
#
# This file is part of Solent.
#
# Solent is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# Solent is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# Solent. If not, see <http://www.gnu.org/licenses/>.
#
# // overview
# Useful when you are looking to identify a line of text as it comes. This
# class can be run against streams, and issues a callback each time it finds
# a line.

import types

STANDARD_ENDINGS = (
    0x00,   # nul
    0x0a,   # newline
    0x04)   # ctrl+d

class CsLineFinderEvent:
    def __init__(self):
        self.rail_h = None
        self.msg = None

class RailLineFinder:
    "When you get to the end of a line, callback."
    def __init__(self):
        self.endings = STANDARD_ENDINGS
        #
        self.sb = []
        self.cs_line_finder_event = CsLineFinderEvent()
    def call_line_finder_event(self, rail_h, msg):
        self.cs_line_finder_event.rail_h = rail_h
        self.cs_line_finder_event.msg = msg
        self.cb_line_finder_event(
            cs_line_finder_event=self.cs_line_finder_event)
    def zero(self, rail_h, cb_line_finder_event):
        self.rail_h = rail_h
        self.cb_line_finder_event = cb_line_finder_event
        #
        self.sb.clear()
    #
    def accept_bytes(self, bb):
        for b in bb:
            self.accept_string(
                s=chr(b))
    def accept_string(self, s):
        if not isinstance(s, str):
            raise Exception('Wrong type supplied [%s]'%(type(s)))
        for c in s:
            if ord(c) in self.endings:
                msg = ''.join(self.sb)
                self.call_line_finder_event(
                    rail_h=self.rail_h,
                    msg=msg)
                self.clear()
            else:
                self.sb.append(c)
    def get(self):
        '''There are situations where it can be useful to get an incomplete
        line. For example, when you are buffering data, and plotting it to
        a terminal while you do.'''
        return ''.join(self.sb)
    def backspace(self):
        if self.sb:
            self.sb.pop()
    def flush(self):
        msg = ''.join(self.sb)
        line = self.call_line_finder_event(
            rail_h=self.rail_h,
            msg=msg)
        self.clear()
    def clear(self):
        self.sb = []

