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
from testing.util import clock_fake

from solent.redis import rail_resp_parser_new

import sys

MTU = 1500

class Receiver:
    def __init__(self):
        self.events = []
    def cb_resp_head(self, cs_resp_head):
        #
        pass
    def cb_resp_tail(self, cs_resp_tail):
        #
        pass
    def cb_resp_str(self, cs_resp_str):
        msg = cs_resp_str.msg
        #
    def cb_resp_err(self, cs_resp_err):
        msg = cs_resp_err.msg
        #
    def cb_resp_int(self, cs_resp_int):
        value = cs_resp_int.value
        #
    def cb_resp_arr_inc(self, cs_resp_arr_head):
        #
        self.events.append( ('arr_head', '') )
    def cb_resp_arr_dec(self, cs_resp_arr_tail):
        #
        self.events.append( ('arr_tail', '') )

@test
def should_parse_message_to_structure():
    r = Receiver()
    #
    rail_resp_parser = rail_resp_parser_new(
        cb_resp_head=r.cb_resp_head,
        cb_resp_tail=r.cb_resp_tail,
        cb_resp_str=r.cb_resp_str,
        cb_resp_err=r.cb_resp_err,
        cb_resp_int=r.cb_resp_int,
        cb_resp_arr_inc=r.cb_resp_arr_inc,
        cb_resp_arr_dec=r.cb_resp_arr_dec)
    #
    return True

if __name__ == '__main__':
    run_tests(
        unders_file=sys.modules['__main__'].__file__)

