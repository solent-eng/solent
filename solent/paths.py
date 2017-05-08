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

import enum
import os
import sys

def dget_root(*args):
    '''
    Retrieve the root directory for the project. This requires different
    handling for development than runtime, where we might be inside a code
    bundle.
    '''
    if are_we_in_a_pyinstaller_bundle():
        # This is a magic variable set by pyintsaller
        path_nodes = sys._MEIPASS.split(os.sep)
    else:
        dir_here = os.path.realpath(os.path.dirname(__file__))
        path_nodes = dir_here.split(os.sep)[:-1]
    path_nodes.extend(args)
    return os.sep.join(path_nodes)

def dget_static(*args):
    '''
    Retrieve the root directory for the project. This requires different
    handling for development than runtime, where we might be inside a code
    bundle.
    '''
    return dget_root('static', *args)

def dget_wres(*args):
    '''
    Path into the wrap-resources directory. That is, native code in shared
    libraries that we are accessing from python.
    '''
    return dget_root('wres', *args)

