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

from solent import solent_keycode
from solent.log import log

import types

STANDARD_ENDINGS = (
    solent_keycode('nul'),
    solent_keycode('newline'),
    solent_keycode('eot'))

class CsFoundLine:
    def __init__(self):
        self.msg = None

class RailLineFinder:
    "When you get to the end of a line, callback."
    def __init__(self, cb_found_line, endings):
        self.cb_found_line = cb_found_line
        self.endings = endings
        #
        self.cs_found_line = CsFoundLine()
        #
        self.sb = []
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
                self._call_found_line(
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
        line = self._call_found_line(
            msg=msg)
        self.clear()
    def clear(self):
        self.sb = []
    #
    def _call_found_line(self, msg):
        self.cs_found_line.msg = msg
        self.cb_found_line(
            cs_found_line=self.cs_found_line)

def rail_line_finder_new(cb_found_line):
    ob = RailLineFinder(
        cb_found_line=cb_found_line,
        endings=STANDARD_ENDINGS)
    return ob

