#
# console
#
# // overview
# Bundle of stuff you need to put a terminal together. Typically, an
# application developer won't create these directly. Rather you'll call
# curses_term or window_term, and that will give you back an instance of this.
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

class Console(object):
    def __init__(self, keystream, grid_display, width, height):
        self.keystream = keystream
        self.grid_display = grid_display
        self.width = width
        self.height = height
    def screen_update(self, cgrid):
        self.grid_display.update(
            cgrid=cgrid)
    def async_getc(self):
        return self.keystream.async_getc()
    def block_getc(self):
        return self.keystream.block_getc()

def console_new(keystream, grid_display, width, height):
    ob = Console(
        keystream=keystream,
        grid_display=grid_display,
        width=width,
        height=height)
    return ob

