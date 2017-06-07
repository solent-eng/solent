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

from solent.util.rail_line_finder import rail_line_finder_new

class Receiver:
    def __init__(self):
        self.events = []
    def cb_found_line(self, cs_found_line):
        msg = cs_found_line.msg
        #
        self.events.append( ('cb_found_line', msg) )

@test
def should_do_basics():
    receiver = Receiver()
    rail_line_finder = rail_line_finder_new(
        cb_found_line=receiver.cb_found_line)
    #
    rail_line_finder.accept_string(
        s='something')
    assert 0 == len(receiver.events)
    #
    rail_line_finder.accept_string(
        s=' _ abc\ndef')
    assert 1 == len(receiver.events)
    assert receiver.events[0] == (
        'cb_found_line', 'something _ abc')
    #
    rail_line_finder.flush()
    assert 2 == len(receiver.events)
    assert receiver.events[1] == (
        'cb_found_line', 'def')
    #
    return True

