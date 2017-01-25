#
# spin_message_feed (testing)
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

from testing import run_tests
from testing import test

from solent.log import log

from solent import solent_cpair
from solent.console import cgrid_new
from solent.rogue import spin_message_feed_new

HEIGHT = 3
WIDTH = 10

@test
def should_construct():
    mfeed = spin_message_feed_new(
        height=HEIGHT,
        width=WIDTH,
        cpair_new=solent_cpair('white_t'),
        cpair_old=solent_cpair('blue_t'))
    return True

@test
def should_handle_simple_prints():
    cgrid = cgrid_new(
        height=HEIGHT,
        width=WIDTH)
    mfeed = spin_message_feed_new(
        height=HEIGHT,
        width=WIDTH,
        cpair_new=solent_cpair('white_t'),
        cpair_old=solent_cpair('blue_t'))
    mfeed.accept('abc', 0)
    mfeed.accept('def', 0)
    mfeed.accept('ghi', 0)
    mfeed.accept('kjl', 0)
    #
    expect = '\n'.join( [ 'def.......'
                        , 'ghi.......'
                        , 'kjl.......'
                        , ''
                        ] )
    mfeed.get_cgrid(
        cgrid=cgrid,
        nail=(0,0),
        peri=(HEIGHT, WIDTH),
        turn=0)
    result = str(cgrid)
    if expect != result:
        print('// expect')
        print(expect)
        print('// result')
        print(result)
        print('~')
    assert expect == result
    #
    return True

@test
def should_handle_long_lines():
    cgrid = cgrid_new(
        height=HEIGHT,
        width=WIDTH)
    mfeed = spin_message_feed_new(
        height=HEIGHT,
        width=WIDTH,
        cpair_new=solent_cpair('white_t'),
        cpair_old=solent_cpair('blue_t'))
    mfeed.accept('zbcdxefghxwjklx', 0)
    mfeed.accept('ybcdxefghxvjklx', 0)
    #
    expect = '\n'.join( [ 'wjklx.....'
                        , 'ybcdxefghx'
                        , 'vjklx.....'
                        , ''
                        ] )
    mfeed.get_cgrid(
        cgrid=cgrid,
        nail=(0,0),
        peri=(HEIGHT, WIDTH),
        turn=0)
    result = str(cgrid)
    if expect != result:
        print('// expect')
        print(expect)
        print('// result')
        print(result)
        print('~')
    assert expect == result
    #
    return True

@test
def should_scroll():
    cgrid = cgrid_new(
        height=HEIGHT,
        width=WIDTH)
    mfeed = spin_message_feed_new(
        height=HEIGHT,
        width=WIDTH,
        cpair_new=solent_cpair('white_t'),
        cpair_old=solent_cpair('blue_t'))
    mfeed.accept('zbcdxefghxwjklx', 0)
    mfeed.accept('ybcdxefghxvjklx', 0)
    mfeed.scroll()
    #
    expect = '\n'.join( [ 'ybcdxefghx'
                        , 'vjklx.....'
                        , '..........'
                        , ''
                        ] )
    mfeed.get_cgrid(
        cgrid=cgrid,
        nail=(0,0),
        peri=(HEIGHT, WIDTH),
        turn=0)
    result = str(cgrid)
    if expect != result:
        print('// expect')
        print(expect)
        print('// result')
        print(result)
        print('~')
    assert expect == result
    #
    return True

@test
def should_scroll_past_old_messages():
    cgrid = cgrid_new(
        height=HEIGHT,
        width=WIDTH)
    mfeed = spin_message_feed_new(
        height=HEIGHT,
        width=WIDTH,
        cpair_new=solent_cpair('white_t'),
        cpair_old=solent_cpair('blue_t'))
    mfeed.accept('abc', 2)
    mfeed.accept('def', 3)
    mfeed.accept('ghi', 4)
    mfeed.scroll_past(
        turn=2)
    #
    expect = '\n'.join( [ 'def.......'
                        , 'ghi.......'
                        , '..........'
                        , ''
                        ] )
    mfeed.get_cgrid(
        cgrid=cgrid,
        nail=(0,0),
        peri=(HEIGHT, WIDTH),
        turn=0)
    result = str(cgrid)
    if expect != result:
        print('// expect')
        print(expect)
        print('// result')
        print(result)
        print('~')
    assert expect == result
    #
    return True

if __name__ == '__main__':
    run_tests(
        unders_file=sys.modules['__main__'].__file__)


