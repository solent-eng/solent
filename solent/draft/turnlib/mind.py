#
# mind interface
#
# // overview
# Builds objects that correspond to the mind interface
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

import types

def mind_interface(cb_add_key, cb_ready, cb_blocking_memo, cb_is_blocking, cb_turn):
    ob = types.ModuleType('mind')
    ob.add_key = cb_add_key
    ob.ready = cb_ready
    ob.blocking_memo = cb_blocking_memo
    ob.is_blocking = cb_is_blocking
    ob.turn = cb_turn
    return ob

