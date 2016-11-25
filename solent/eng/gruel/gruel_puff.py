#
# gruel_puff
#
# // overview
# Used for expanding gruel-protocol messages from their wire form into
# something that is useful to application software.
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

class GruelPuff:
    def __init__(self, gruel_schema, mtu):
        self.gruel_schema = gruel_schema
        self.mtu = mtu

def gruel_puff_new(gruel_schema, mtu):
    ob = GruelPuff(
        gruel_schema=gruel_schema,
        mtu=mtu)
    return ob

