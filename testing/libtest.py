#
# utest
#
# There's lots wrong with this, but it's effective for the moment.
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

import traceback

TESTS = []
def test(fn):
    def go():
        print('')
        print('// --------------------------------------------------------')
        print('//   %s'%(fn.__name__))
        print('// --------------------------------------------------------')
        try:
            fn()
            print('[SUCCESS]')
        except:
            traceback.print_exc()
            print('[FAILED]')
        print('')
    global TESTS
    TESTS.append(go)
    return fn

def run_tests():
    global TESTS
    for t in TESTS:
        t()
    # hack. can fix this later. this clears out all the tests in the current
    # module so that it will be empty for the next module that comes along.
    # (we can make this nice later, but for now it's fine)
    def clear_all_tests():
        while TESTS:
            TESTS.pop()
    clear_all_tests()

