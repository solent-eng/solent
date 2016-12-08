#
# cformat
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

#
# From http://ascii-table.com/ansi-escape-sequences.php
BG_COLOURS = { 'black': 40
             , 'red': 41
             , 'green': 42
             , 'yellow': 43
             , 'blue': 44
             , 'magenta': 45
             , 'cyan': 46
             , 'white': 47
             , 'trans': 49
             }

FG_COLOURS = { 'black': 30
             , 'red': 31
             , 'green': 32
             , 'yellow': 33
             , 'blue': 34
             , 'magenta': 35
             , 'cyan': 36
             , 'white': 37
             }

ENDC = '\033[0m'

def cformat(string, fg, bg='black', bold=False):
    if bold:
        ibold = 1
    else:
        ibold = 3
    return '\033[%s;%s;%sm%s%s'%( FG_COLOURS[fg]
                                , BG_COLOURS[bg]
                                , ibold
                                , string
                                , ENDC
                                )

