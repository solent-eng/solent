#
# wrap_shared_lib: demonstrates wrapping a shared library function in python.
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

from solent import dget_wres
from solent import init_ext_fn
from solent import log

from ctypes import *

#PATH_SO = dget_wres('draft', 'wrap', 'api.so')
PATH_SO = dget_wres('draft', 'wrap', 'api.dll')

class Wrap:
    def __init__(self):
        self.clib = cdll.LoadLibrary(PATH_SO)
        #
        self.fn_hello = init_ext_fn(
            rtype=c_char_p,
            so_fn=self.clib.hello,
            alist=[c_char_p])
    def hello(self, what):
        return self.fn_hello(what)

def wrap_new():
    ob = Wrap()
    return ob

def main():
    w = wrap_new()
    bb = w.hello(
        what=bytes("this", 'utf8'))
    log('bb %s'%bb)

if __name__ == '__main__':
    main()

