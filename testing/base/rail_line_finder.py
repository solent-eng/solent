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

from solent import RailLineFinder
from solent import run_tests
from solent import test

class Receiver:
    def __init__(self):
        self.events = []
    def cb_line_finder_event(self, cs_line_finder_event):
        rail_h = cs_line_finder_event.msg
        msg = cs_line_finder_event.msg
        #
        self.events.append( ('cb_line_finder_event', msg) )

@test
def should_do_basics():
    receiver = Receiver()
    rail_line_finder = RailLineFinder()
    rail_line_finder.zero(
        rail_h='line_finder.only',
        cb_line_finder_event=receiver.cb_line_finder_event)
    #
    rail_line_finder.accept_string(
        s='something')
    assert 0 == len(receiver.events)
    #
    rail_line_finder.accept_string(
        s=' _ abc\ndef')
    assert 1 == len(receiver.events)
    assert receiver.events[0] == (
        'cb_line_finder_event', 'something _ abc')
    #
    rail_line_finder.flush()
    assert 2 == len(receiver.events)
    assert receiver.events[1] == (
        'cb_line_finder_event', 'def')
    #
    return True

