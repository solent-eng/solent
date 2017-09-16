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

from solent import log
from solent.rogue.swamp_monster.chart import chart_new
from solent.test import run_tests
from solent.test import test

import sys

@test
def should_show_differences():
    n = chart_new(3, 3)
    p = chart_new(3, 3)
    #
    n.put(
        spot=(0,0),
        sigil_h='sigil_z')
    #
    n.put(
        spot=(0,1),
        sigil_h='sigil_y')
    p.put(
        spot=(0,1),
        sigil_h='sigil_y')
    #
    n.put(
        spot=(0,2),
        sigil_h='sigil_x')
    p.put(
        spot=(0,2),
        sigil_h='sigil_q')
    #
    p.put(
        spot=(1,0),
        sigil_h='sigil_w')
    #
    expect = [
        ((0, 0), 'sigil_z'),
        ((0, 2), 'sigil_x'),
        ((1, 0), None)]
    res = n.show_differences_to(
        chart=p)
    assert expect == res
    #
    return True

if __name__ == '__main__':
    run_tests()

