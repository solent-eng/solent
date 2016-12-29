#
# cursor
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

class Cursor(object):
    def __init__(self, fn_s, fn_e, fn_c, fn_cpair):
        self.fn_s = fn_s
        self.fn_e = fn_e
        self.fn_c = fn_c
        self.fn_cpair = fn_cpair
    def get_s(self):
        return self.fn_s()
    def get_e(self):
        return self.fn_e()
    def get_c(self):
        return self.fn_c()
    def get_cpair(self):
        return self.fn_cpair()

def cursor_new(fn_s, fn_e, fn_c, fn_cpair):
    ob = Cursor(
        fn_s=fn_s,
        fn_e=fn_e,
        fn_c=fn_c,
        fn_cpair=fn_cpair)
    return ob

