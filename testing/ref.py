#
# ref_store
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

from solent import mempool_new
from solent import ref_create
from solent import ref_lookup
from solent import ref_acquire
from solent import ref_release
from solent.log import log
from solent.test import run_tests
from solent.test import test

@test
def should_acquire_and_release():
    source = 'abc'
    ref = ref_create(
        bb=source)
    ref_acquire(
        ref=ref)
    taken = ref_lookup(
        ref=ref)
    assert taken == source
    #
    # see that it gets cleaned up
    ref_release(
        ref=ref)
    b_exception = False
    try:
        ref_lookup(
            ref=ref)
    except:
        b_exception = True
    if not b_exception:
        raise Exception("looks like it did not get cleaed up")
    #
    return True

if __name__ == '__main__':
    run_tests()

