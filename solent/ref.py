#
# refstore
#
# // overview
# This class won't exist in a future C-style implementation. It's necessary
# in python so that we can pass references around in such a way that they
# do not live in memory forever. We have this refstore, which maintains
# aquire/release counts over references. Then the python implementations of
# mempool/sip touch the refstore.
#
# The acquire/release model here is not quite the same as in objective-c.
# When you create a reference, it starts at 0. But it doesn't get cleaned up.
# It gets cleaned up when a release is done on it that takes it to 0.
#
# Remember: this is a sequencer architecture design that happens to currently
# be written in python. It's only a matter of time until we port it to
# something low-garbage, and to leave the door open to that there are places
# where we need to be in control of our memory.
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

from solent.util import uniq

class RefStore:
    def __init__(self):
        # ref int vs int
        self.acrelease_counts = {}
        # ref int vs data
        self.store = {}
    def create(self, data):
        ref = uniq()
        self.acrelease_counts[ref] = 0
        self.store[ref] = data
        return ref
    def lookup(self, ref):
        if ref not in self.store:
            raise Exception('Store does not have ref [%s]'%(ref))
        return self.store[ref]
    def acquire(self, ref):
        self.acrelease_counts[ref] += 1
    def release(self, ref):
        self.acrelease_counts[ref] -= 1
        if 0 == self.acrelease_counts[ref]:
            del self.acrelease_counts[ref]
            del self.store[ref]

REF_STORE = None
def _store_singleton():
    global REF_STORE
    if None == REF_STORE:
        REF_STORE = RefStore()
    return REF_STORE

def ref_create(data):
    ref_store = _store_singleton()
    ref = ref_store.create(data)
    return ref

def ref_lookup(ref):
    ref_store = _store_singleton()
    data = ref_store.lookup(ref)
    return data

def ref_acquire(ref):
    ref_store = _store_singleton()
    ref_store.acquire(ref)

def ref_release(ref):
    ref_store = _store_singleton()
    ref_store.release(ref)

