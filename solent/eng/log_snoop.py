#
# log snoop
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

from solent.log import log

from collections import deque

class LogSnoop:
    '''
    Logs any message seen on the associated nearcast.
    '''
    def __init__(self, nearcast_schema):
        self.b_enabled = True
        self.nearcast_schema = nearcast_schema
    def disable(self):
        self.b_enabled = False
    def at_turn(self, activity):
        pass
    def on_nearcast_message(self, cog_h, message_h, d_fields):
        if not self.b_enabled:
            return
        def format_message():
            sb = []
            sb.append('%s>%s'%(cog_h, message_h))
            for key in self.nearcast_schema[message_h]:
                sb.append('%s:%s'%(key, d_fields[key]))
            return '/'.join(sb)
        nice = format_message()
        log(nice)

def log_snoop_new(nearcast_schema):
    ob = LogSnoop(
        nearcast_schema=nearcast_schema)
    return ob

