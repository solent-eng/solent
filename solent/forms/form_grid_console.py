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

from solent import Ns

class FormGridConsole:
    def __init__(self, impl):
        self.impl = impl
        #
        self.cs_grid_console_splat = Ns()
        self.cs_grid_console_kevent = Ns()
        self.cs_grid_console_mevent = Ns()
        self.cs_grid_console_closed = Ns()
    def call_grid_console_splat(self, zero_h, msg):
        self.cs_grid_console_splat.zero_h = zero_h
        self.cs_grid_console_splat.msg = msg
        self.impl.cb_grid_console_splat(
            cs_grid_console_splat=self.cs_grid_console_splat)
    def call_grid_console_kevent(self, zero_h, keycode):
        # Key event. Keycode needs to reflect the values used by
        # solent_keycode.
        self.cs_grid_console_kevent.zero_h = zero_h
        self.cs_grid_console_kevent.keycode = keycode
        self.impl.cb_grid_console_kevent(
            cs_grid_console_kevent=self.cs_grid_console_kevent)
    def call_grid_console_mevent(self, zero_h, lb, mb, rb, x, y):
        # Mouse event. x and y values should be relative to the console
        # window's nail (top left). Buttons should be 0 or 1.
        self.cs_grid_console_mevent.zero_h = zero_h
        self.cs_grid_console_mevent.lb = lb
        self.cs_grid_console_mevent.mb = mb
        self.cs_grid_console_mevent.rb = rb
        self.cs_grid_console_mevent.x = x
        self.cs_grid_console_mevent.y = y
        self.impl.cb_grid_console_mevent(
            cs_grid_console_mevent=self.cs_grid_console_mevent)
    def call_grid_console_closed(self, zero_h):
        self.cs_grid_console_closed.zero_h = zero_h
        self.impl.cb_grid_console_closed(
            cs_grid_console_closed=self.cs_grid_console_closed)
    #
    def send(self, cgrid):
        """
        Ensure the contents of the supplied cgrid are shown on
        the grid.
        """
        return self.impl.send(
            cgrid=cgrid)
    def close(self):
        return self.impl.close()

