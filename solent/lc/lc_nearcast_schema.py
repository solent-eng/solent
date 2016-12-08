#
# lc_nearcast_schema
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

from solent.eng import nearcast_schema_new
from solent.log import log

I_LC_NEARCAST_SCHEMA = '''
    i message h
        i field h

    message lc_line
        field line

    message start_gruel_server

    message stop_gruel_server
'''

def lc_nearcast_schema_new():
    ob = nearcast_schema_new(
        i_nearcast=I_LC_NEARCAST_SCHEMA)
    return ob

