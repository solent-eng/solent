#
# spin_message_feed
#
# // overview
# This accepts text messages, and then renders them to a cgrid. Imagine text
# as it is coming out of an old-fashioned printer, on a feed of paper.
#
# There are two general use-cases for retrieving data from this:
# * You can call list_messages, and get back a list of current messages
# * You can call get_cgrid, and it will populate your supplied grid
#
# xxx needs a refactor: remove spin from the naming
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

from solent.console import cgrid_new
from solent.log import log

from collections import deque

class SpinMessageFeed:
    def __init__(self, height, width, cpair_new, cpair_old):
        self.height = height
        self.width = width
        self.cpair_new = cpair_new
        self.cpair_old = cpair_old
        #
        self.cgrid = cgrid_new(
            height=height,
            width=width)
        self.q_lines = deque()
    def clear(self):
        while self.q_lines:
            self.scroll()
    def accept(self, message, turn):
        nail = 0
        peri = nail+self.width
        while len(message) > peri:
            self._write(
                text=message[nail:peri],
                turn=turn)
            nail = peri
            peri = peri + self.width
        self._write(
            text=message[nail:peri],
            turn=turn)
    def scroll(self):
        self.q_lines.popleft()
    def scroll_past(self, turn):
        while self.q_lines:
            first_pair = self.q_lines[0]
            message_turn = first_pair[1]
            if message_turn <= turn:
                self.scroll()
            else:
                break
    def get_height(self):
        return len(self.q_lines)
    def list_messages(self):
        sb = []
        for (message, turn) in self.q_lines:
            sb.append(message)
        return sb
    def get_cgrid(self, cgrid, nail, peri, turn):
        self.cgrid.clear()
        for idx, (line, mturn) in enumerate(self.q_lines):
            if mturn == turn:
                cpair = self.cpair_new
            else:
                cpair = self.cpair_old
            self.cgrid.put(
                drop=idx,
                rest=0,
                s=line,
                cpair=cpair)
        cgrid.blit(
            self.cgrid,
            nail=nail,
            peri=peri)
    def _write(self, text, turn):
        self.q_lines.append( (text, turn) )
        while len(self.q_lines) > self.height:
            self.q_lines.popleft()

def spin_message_feed_new(height, width, cpair_new, cpair_old):
    ob = SpinMessageFeed(
        height=height,
        width=width,
        cpair_new=cpair_new,
        cpair_old=cpair_old)
    return ob

