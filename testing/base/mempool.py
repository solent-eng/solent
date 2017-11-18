#
# mempool
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

from solent import Mempool
from solent import log
from solent import run_tests
from solent import test

@test
def should_get_and_return():
    mempool = Mempool()
    #
    # get
    sip_a = mempool.alloc(101)
    sip_a.arr[0] = 123
    assert 123 == sip_a.arr[0]
    assert 101 == sip_a.size
    assert 1 == mempool.ltotal
    #
    # clone
    sip_b = mempool.clone(
        sip=sip_a)
    assert 123 == sip_a.arr[0]
    assert 123 == sip_b.arr[0]
    assert 101 == sip_b.size
    assert 2 == mempool.ltotal
    #
    # change the cloned one: check it's different memory
    sip_b.arr[0] = 15
    assert 123 == sip_a.arr[0]
    assert 15 == sip_b.arr[0]
    #
    # free
    mempool.free(
        sip=sip_a)
    mempool.free(
        sip=sip_b)
    assert 0 == mempool.ltotal
    assert 2 == len(mempool.pool[101])
    #
    # check that it is issuing from the pool, not making unnecessary
    # allocations
    sip_c = mempool.alloc(101)
    assert 1 == len(mempool.pool[101])
    #
    return True

if __name__ == '__main__':
    run_tests()

