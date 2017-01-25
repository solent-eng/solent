#
# cpair
#
# // overview
# Enumeration for colourpairs in the platform. By having a centralised
# enumeration, we can try to make the user experiences fairly consistent
# across different types of console (pygame, ncurses, etc).
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

import enum

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

def solent_cpair(name):
    '''
    Pass in the name of a member of e_cpair. This uses reflection to look it
    up from the enumeration itself, and returns the value of the selected
    item.
    '''
    l = dir(e_cpair)
    if name not in l:
        raise Exception("e_cpair.%s does not exist"%(name))
    return getattr(e_cpair, name).value

