#
# lc_nearcast_schema (testing)
#
# // overview
# The nearcast schema for the line console server functionality.
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
from testing.eng import engine_fake
from testing.util import clock_fake

from solent.eng import activity_new
from solent.eng import cs
from solent.lc import lc_nearcast_schema_new
from solent.log import log
from solent.log import hexdump_bytearray
from solent.util import uniq

import sys

@test
def should_not_crash():
    nearcast_schema = lc_nearcast_schema_new()
    #
    return True

if __name__ == '__main__':
    run_tests(
        unders_file=sys.modules['__main__'].__file__)

