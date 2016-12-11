#!/usr/bin/env python3
#
# line finder
#
# // overview
# Useful when you are looking to identify a line of text as it comes. This
# class can be run against streams, and issues a callback each time it finds
# a line.
#
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

from solent.log import log

import types

class LineFinder:
    "When you get to the end of a line, callback."
    def __init__(self, cb_line):
        self.cb_line = cb_line
        #
        self.sb = []
    def clear(self):
        self.sb = []
    def accept_bytes(self, barr):
        for b in barr:
            self.accept_string(
                s=chr(b))
    def accept_string(self, s):
        if not isinstance(s, str):
            raise Exception('Wrong type supplied [%s]'%(type(s)))
        for c in s:
            if c == '\n':
                self.cb_line(''.join(self.sb))
                self.sb = []
            else:
                self.sb.append(c)

def line_finder_new(cb_line):
    ob = LineFinder(
        cb_line=cb_line)
    return ob

