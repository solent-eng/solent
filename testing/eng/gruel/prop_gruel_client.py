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

from solent.eng import prop_gruel_client_new

def create_prop_gruel_client():
    engine = engine_fake()
    addr = '127.0.0.1'
    port = 1234
    prop_gruel_client = prop_gruel_client_new(
        engine=engine)
    return prop_gruel_client

@test
def test_connection():
    prop_gruel_client = create_prop_gruel_client()

if __name__ == '__main__':
    run_tests()

