#
# ip_validator (testing)
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

from solent.console import cgrid_new
from solent.console import e_colpair

from testing import run_tests
from testing import test
from testing.eng import engine_fake
from testing.util import clock_fake

from solent.eng import ip_validator_new

import sys

DEFAULT_CPAIR = e_colpair.white_t

def cgrid_console_print(cgrid):
    for h in range(cgrid.height):
        nail = (h*cgrid.width)
        peri = nail + cgrid.width
        spots = cgrid.spots[nail:peri]
        line = ''.join( [s.c for s in spots] )
        print('%2s|%s'%(h, line))

def cgrid_populate(cgrid, c):
    for drop in range(cgrid.height):
        cgrid.put(
            drop=drop,
            rest=0,
            s=c*cgrid.height,
            cpair=DEFAULT_CPAIR)

@test
def should_create_two_simple_grids():
    grid_a = cgrid_new(5, 5)
    cgrid_populate(grid_a, '-')
    cgrid_console_print(grid_a)
    #
    grid_b = cgrid_new(3, 3)
    cgrid_populate(grid_b, '|')
    cgrid_console_print(grid_b)
    #
    return True

@test
def should_copy_one_grid_onto_another():
    grid_a = cgrid_new(5, 5)
    cgrid_populate(grid_a, '*')
    #
    grid_b = cgrid_new(3, 3)
    grid_b.put(0, 0, 'a', DEFAULT_CPAIR)
    grid_b.put(0, 1, 'b', DEFAULT_CPAIR)
    grid_b.put(0, 2, 'c', DEFAULT_CPAIR)
    grid_b.put(1, 0, 'd', DEFAULT_CPAIR)
    grid_b.put(1, 1, 'e', DEFAULT_CPAIR)
    grid_b.put(1, 2, 'f', DEFAULT_CPAIR)
    grid_b.put(2, 0, 'g', DEFAULT_CPAIR)
    grid_b.put(2, 1, 'h', DEFAULT_CPAIR)
    grid_b.put(2, 2, 'i', DEFAULT_CPAIR)
    #
    grid_a.blit(grid_b)
    cgrid_console_print(grid_a)
    #
    return True

@test
def should_do_a_truncated_copy_on_the_right_side():
    grid_a = cgrid_new(5, 5)
    zyx = [chr(i+65) for i in range(26)]
    zyx.reverse()
    for i in range(25):
        l = zyx[i]
        drop = int(i / 5)
        rest = i % 5
        grid_a.put(
            drop=drop,
            rest=rest,
            s=l.lower(),
            cpair=DEFAULT_CPAIR)
    #
    grid_b = cgrid_new(3, 3)
    grid_b.put(0, 0, '0', DEFAULT_CPAIR)
    grid_b.put(0, 1, '1', DEFAULT_CPAIR)
    grid_b.put(0, 2, '2', DEFAULT_CPAIR)
    grid_b.put(1, 0, '3', DEFAULT_CPAIR)
    grid_b.put(1, 1, '4', DEFAULT_CPAIR)
    grid_b.put(1, 2, '5', DEFAULT_CPAIR)
    grid_b.put(2, 0, '6', DEFAULT_CPAIR)
    grid_b.put(2, 1, '7', DEFAULT_CPAIR)
    grid_b.put(2, 2, '8', DEFAULT_CPAIR)
    #
    grid_a.blit(
        src_cgrid=grid_b,
        nail=(1,3))
    cgrid_console_print(grid_a)
    #
    return True

@test
def should_do_a_truncated_copy_on_the_bottom_border():
    grid_a = cgrid_new(5, 5)
    zyx = [chr(i+65) for i in range(26)]
    zyx.reverse()
    for i in range(25):
        l = zyx[i]
        drop = i / 5
        rest = i % 5
        grid_a.put(
            drop=drop,
            rest=rest,
            s=l.lower(),
            cpair=DEFAULT_CPAIR)
    #
    grid_b = cgrid_new(3, 3)
    grid_b.put(0, 0, '0', DEFAULT_CPAIR)
    grid_b.put(0, 1, '1', DEFAULT_CPAIR)
    grid_b.put(0, 2, '2', DEFAULT_CPAIR)
    grid_b.put(1, 0, '3', DEFAULT_CPAIR)
    grid_b.put(1, 1, '4', DEFAULT_CPAIR)
    grid_b.put(1, 2, '5', DEFAULT_CPAIR)
    grid_b.put(2, 0, '6', DEFAULT_CPAIR)
    grid_b.put(2, 1, '7', DEFAULT_CPAIR)
    grid_b.put(2, 2, '8', DEFAULT_CPAIR)
    #
    grid_a.blit(
        src_cgrid=grid_b,
        nail=(3,1))
    cgrid_console_print(grid_a)
    #
    return True

@test
def should_copy_fine_despite_us_not_supplying_a_nail_param_to_blit():
    grid_a = cgrid_new(5, 5)
    zyx = [chr(i+65) for i in range(26)]
    zyx.reverse()
    for i in range(25):
        l = zyx[i]
        drop = i / 5
        rest = i % 5
        grid_a.put(
            drop=drop,
            rest=rest,
            s=l.lower(),
            cpair=DEFAULT_CPAIR)
    #
    grid_b = cgrid_new(3, 3)
    grid_b.put(0, 0, '0', DEFAULT_CPAIR)
    grid_b.put(0, 1, '1', DEFAULT_CPAIR)
    grid_b.put(0, 2, '2', DEFAULT_CPAIR)
    grid_b.put(1, 0, '3', DEFAULT_CPAIR)
    grid_b.put(1, 1, '4', DEFAULT_CPAIR)
    grid_b.put(1, 2, '5', DEFAULT_CPAIR)
    grid_b.put(2, 0, '6', DEFAULT_CPAIR)
    grid_b.put(2, 1, '7', DEFAULT_CPAIR)
    grid_b.put(2, 2, '8', DEFAULT_CPAIR)
    #
    grid_a.blit(
        src_cgrid=grid_b)
    cgrid_console_print(grid_a)
    #
    return True

if __name__ == '__main__':
    run_tests(
        unders_file=sys.modules['__main__'].__file__)

