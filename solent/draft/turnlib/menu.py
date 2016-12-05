#
# menu
#
# // overview
# stores a unique trigger character against some text and a callback.
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

from collections import OrderedDict as od

class Menu(object):
    def __init__(self):
        # c vs (text, fn_callback)
        self.d = od()
    def clear(self):
        keys = self.d.keys()
        for k in keys:
            del self.d[k]
    def add(self, key, text, fn_callback):
        if key in self.d:
            raise Exception("Can't add duplicate key. [%s]"%(key))
        if 1 != len(key):
            raise Exception("Key must be a single char [%s] "%(key))
        self.d[key] = (text, fn_callback)
    def has_key(self, key):
        return key in self.d
    def get_keys(self):
        return self.d.keys()
    def get_desc(self, key):
        return self.d[key][0]
    def get_callback(self, key):
        return self.d[key][1]
    def get_lines(self):
        sb = []
        for k, v in self.d.items():
            (text, fn_callback) = v
            sb.append('[%s] %s'%(k, text))
        return sb

def menu_new():
    ob = Menu()
    return ob

