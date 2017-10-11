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
# // overview
# Simple, effective bootstrap for a testing system.

from os import path
import sys
import traceback

TESTS = []
def test(fn):
    def go():
        print('// %s'%(fn.__name__))
        b_exit_condition = False
        try:
            res = fn()
            if res == True:
                print('[SUCCESS]')
            else:
                print('[FAILED]')
                b_exit_condition = True
        except:
            traceback.print_exc()
            print('[ABORTED]')
            b_exit_condition = True
        print('')
        if b_exit_condition:
            sys.exit(1)
    global TESTS
    TESTS.append(go)
    return fn

def hacky_module_name(unders_file):
    name = path.abspath(sys.modules['__main__'].__file__)
    care = 'solent'.join( name.split('solent')[1:] )
    # get rid of the leading slash
    care = care[1:]
    return care

def have_tests():
    global TESTS
    if 0 == len(TESTS):
        return False
    return True

def clear_tests():
    global TESTS
    while TESTS:
        TESTS.pop()

def run_tests():
    global TESTS
    #
    for t in TESTS:
        t()
    # hack. can fix this later. this clears out all the tests in the current
    # module so that it will be empty for the next module that comes along.
    # (we can make this nice later, but for now it's fine)
    def clear_all_tests():
        while TESTS:
            TESTS.pop()
    clear_all_tests()

