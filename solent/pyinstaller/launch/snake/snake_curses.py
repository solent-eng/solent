#!/usr/bin/env python3
#
# snake
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

from solent.release.snake import game

from solent.log import log

def am_i_in_a_pyinsaller_bundle():
    import sys
    if getattr(sys, 'frozen', False):
        log('has frozen')
    else:
        log('no frozen')

def main():
    game(
        console_type='curses')

if __name__ == '__main__':
    main()

