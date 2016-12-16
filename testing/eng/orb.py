#
# orb (testing)
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

from solent.eng import nearcast_schema_new
from solent.eng import orb_new

I_NEARCAST_EXAMPLE = '''
    i message h
        i field h

    # declare a message called organisation that takes certain fields
    message organisation
        field h
        field name
        field address

    # declare a message called person that takes certain fields
    message person
        field h
        field firstname
        field lastname
        field age
        field organisation_h
'''

@test
def should_construct():
    engine = engine_fake()
    nearcast_schema = nearcast_schema_new(
        i_nearcast=I_NEARCAST_EXAMPLE)
    orb = engine.init_orb(
        orb_h='app',
        nearcast_schema=nearcast_schema)
    #
    return True

if __name__ == '__main__':
    run_tests(
        unders_file=sys.modules['__main__'].__file__)

