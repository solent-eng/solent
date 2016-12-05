#
# logbook
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

from collections import deque

class Entry(object):
    def __init__(self, text):
        self.text = text
        #
        self.b_new = True

class Logbook(object):
    def __init__(self, capacity):
        self.capacity = capacity
        #
        self.q = deque()
        self.t = 0
    def log(self, t, s):
        self.t = t
        self.q.append(Entry(s))
        if len(self.q) > self.capacity:
            self.q.popleft()
    def recent(self):
        out = []
        for itm in self.q:
            if itm.b_new:
                out.append(itm.text)
                itm.b_new = False
        return out

def logbook_new(capacity):
    ob = Logbook(
        capacity=capacity)
    return ob

