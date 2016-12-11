#
# enumerations for terminal package
#
# // overview
# constants for the term package
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

class e_colpair(enum.Enum):
    "colour pairs"
    red_t         = 1000
    green_t       = 1001
    yellow_t      = 1002
    blue_t        = 1003
    purple_t      = 1004
    cyan_t        = 1005
    white_t       = 1006
    t_red         = 1007
    t_green       = 1008
    t_yellow      = 1009
    white_blue    = 1010
    white_purple  = 1011
    black_cyan    = 1012
    t_white       = 1013

class e_boxtype(enum.Enum):
    line          = 2000
    edge          = 2001
    void          = 2002
    hash          = 2003
    stop          = 2004

class e_keycode(enum.Enum):
    backspace     = chr(0x8)
    newline       = chr(0xa)

