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
#
# // overview
# Offers roguelike console display through native Windows widgets.
#

from solent import solent_cpair
from solent import solent_keycode
from solent import dget_static
from solent.console import Cgrid
from solent.console import iconsole_new
from solent.console import keystream_new
from solent.log import log

from solent.exceptions import SolentQuitException

from collections import deque
import os

class Console:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        #
        raise Exception('nyi')
    def on_close(self):
        raise Exception('nyi')
    def get_last_lmousedown(self):
        raise Exception('nyi')
    def get_last_lmouseup(self):
        raise Exception('nyi')
    def get_last_rmousedown(self):
        raise Exception('nyi')
    def get_last_rmouseup(self):
        raise Exception('nyi')
    def get_grid_display(self):
        raise Exception('nyi')
    def get_keystream(self):
        raise Exception('nyi')
    def async_get_keycode(self):
        raise Exception('nyi')
    def block_get_keycode(self):
        raise Exception('nyi')

def create(width, height):
    console = Console(
        width=width,
        height=height)
    #
    ob = iconsole_new(
        keystream=window_console.get_keystream(),
        grid_display=window_console.get_grid_display(),
        width=width,
        height=height,
        cb_last_lmouseup=window_console.get_last_lmouseup,
        cb_last_lmousedown=window_console.get_last_lmousedown,
        cb_last_rmouseup=window_console.get_last_rmouseup,
        cb_last_rmousedown=window_console.get_last_rmousedown,
        cb_close=window_console.on_close)
    return ob
