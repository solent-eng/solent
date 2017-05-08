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

from solent.test import run_tests
from solent.test import test

from fake.eng import fake_engine_new

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
    engine = fake_engine_new()
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST_EXAMPLE)
    #
    return True

if __name__ == '__main__':
    run_tests()

