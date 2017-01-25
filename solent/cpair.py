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
    """Colour pairs. The numbering system has been selected to try and make
    things easy for limited-colour consoles who want to round-down to make
    a best-fit for their available colours. This way we should be able to
    make later additions to the available colours without causing hard
    breaks on older curses tweaking.
    
    To understand where I started, see the colour diagram at
    https://en.wikipedia.org/wiki/File:Color_star-en_(tertiary_names).svg
    Seems to be the RYB colour model.
    """
    # 50-100 is shares of grey, ending in white
    grey            = 66

    # 100-200 is colour shares on black background
    white           = 100
    red             = 120
    vermilion       = 125  # FF4500
    orange          = 130  # FFA500
    amber           = 135
    yellow          = 140
    chartreuse      = 145  # 7FFF00
    green           = 150
    teal            = 155
    blue            = 160
    violet          = 165
    purple          = 170
    magenta         = 175

    # 200-300 is shades of grey on a very-light-but-unspecified background
    black_info      = 200
    grey_info       = 250
    # 300-400 is shares of colour on an unspecified-colour background
    green_info      = 350

    # 400 is an alarm colour pair
    alarm           = 400
 
def solent_cpair_pairs():
    """Returns (cpair_value, cpair_name), sorted."""
    lst = []
    for name in dir(e_cpair):
        if name.startswith('__'):
            continue
        print('name %s'%name)
        v = getattr(e_cpair, name).value
        lst.append( (v, name) )
    lst.sort()
    return lst

def solent_name_cpair(value):
    return e_cpair[value]

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

class e_reduced_cpair(enum.Enum):
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

def solent_reduce_cpair_to_basic_code(value):
    """In situations where you have a basic colour palette environment (e.g.
    curses) you want a simple way to reduce from the fancy colour to
    something that works for you."""



