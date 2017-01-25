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

from .exceptions import SolentQuitException
from .mempool import mempool_new

from .keycode import solent_keycode
from .cpair import solent_cpair

from .ref import ref_create
from .ref import ref_lookup
from .ref import ref_acquire
from .ref import ref_release

import enum
import os
import sys

class e_cpair(enum.Enum):
    "colour pairs"
    red_t         = 0
    green_t       = 1
    yellow_t      = 2
    blue_t        = 3
    purple_t      = 4
    cyan_t        = 5
    white_t       = 6
    t_red         = 7
    t_green       = 8
    t_yellow      = 9
    white_blue    = 10
    white_purple  = 11
    black_cyan    = 12
    t_white       = 13

def are_we_in_a_pyinsaller_bundle():
    # In pyinstaller bundles, there is a magic variable called frozen
    # attached to sys.
    if getattr(sys, 'frozen', False):
        return True
    else:
        return False

def dget_root(*args):
    '''
    '''
    if are_we_in_a_pyinsaller_bundle():
        # This is a magic variable set by pyintsaller
        path_nodes = sys._MEIPASS.split(os.sep)
    else:
        dir_here = os.path.realpath(os.path.dirname(__file__))
        path_nodes = dir_here.split(os.sep)[:-1]
    path_nodes.extend(args)
    return os.sep.join(path_nodes)

def dget_static(*args):
    return dget_root('static', *args)

def dget_wres(*args):
    '''
    Path into the wrap-resources directory. That is, native code in shared
    libraries that we are accessing from python.
    '''
    return dget_root('wres', *args)

