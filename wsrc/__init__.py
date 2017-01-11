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

import os

def dget_root(*args):
    '''
    '''
    dir_here = os.path.realpath(os.path.dirname(__file__))
    path = dir_here.split(os.sep)[:-1]
    path.extend(args)
    return os.sep.join(path)

def dget_wsrc(*args):
    return dget_root('wsrc', *args)

def dget_wres(*args):
    return dget_root('wres', *args)

def path_from_wsrc_package(nodes):
    '''
    Supply __package__ to this, from a wsrc path.
    '''
    return dget_root(*nodes)

