#
# mempool
#
# // overview
# Allows us to get and retrieve mutable byte arrays.
#
# Remember: this is a sequencer architecture design that happens to currently
# be written in python. It's only a matter of time until we port it to
# something low-garbage, and to leave the door open to that there are places
# where we need to be in control of our memory. If it makes it easier, try to
# think of this as a C codebase that happens to currently be implemented in
# python.
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

from .sip import sip_new

class Mempool:
    def __init__(self):
        # int size vs [sip]
        self.pool = {}
        # int size vs int count
        self.lent = {}
        self.ltotal = 0
    def alloc(self, size):
        'Returns a sip of size.'
        if size not in self.pool:
            self.pool[size] = []
            self.lent[size] = 0
        self.lent[size] += 1
        self.ltotal += 1
        if len(self.pool[size]) == 0:
            sip = sip_new(size)
        else:
            sip = self.pool[size].pop()
        # This is part of a hack to allow sip references in this python
        # implementation. See section in sip.py.
        sip._ref_handle = object()
        return sip
    def clone(self, sip):
        '''Allocate a new sip, copy the supplied sip's arr to it, and
        then return that newly-allocated sip.'''
        nsip = self.alloc(
            size=sip.size)
        nsip.arr[:] = sip.arr
        return nsip
    def free(self, sip):
        self.ltotal -= 1
        self.lent[sip.size] -= 1
        self.pool[sip.size].append(sip)
        # This is part of a hack to allow sip references in this python
        # implementation. See section in sip.py.
        sip._ref_handle = None

def mempool_new():
    ob = Mempool()
    return ob

