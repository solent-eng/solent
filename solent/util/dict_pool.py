#
# experimental. possibly wacky. not yet completely given up on the idea.
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

class DictPool(object):
    def __init__(self, solent_type, keys, initial_allocation):
        self.solent_type = solent_type
        self.keys = keys
        #
        self.store = []
        for i in range(initial_allocation):
            self._create()
    def _create(self):
        d = {}
        for k in keys:
            d[k] = None
        d['__solent_type__'] = self.solent_type
        self.store.append(d)
    def get(self):
        if not self.store:
            self._create()
        ob = self.store.pop()
        return ob
    def put(self, d):
        self.store.append(d)

def dict_pool_new(solent_type, keys, initial_allocation):
    '''
    solent_type: an arbitrary string that should clearly identify the purpose
    of each dictionary.
    keys: a set or list of field names.
    '''
    ob = DictPool(
        solent_type=solent_type,
        keys=keys,
        initial_allocation=initial_allocation)
    return ob

