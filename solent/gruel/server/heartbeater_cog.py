#
# heartbeater
#
# // overview
# responsible for both making heartbeats. in practice, if both sides are
# trying to make heartbeats regularly there is no need to watch for them.
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

from solent.eng import ip_validator_new
from solent.log import log

class HeartbeaterCog(object):
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.b_active = False
        self.t_last_heartbeat = None
    #
    def on_announce_login(self, max_packet_size, max_fulldoc_size):
        self.b_active = True
        self.t_last_heartbeat = self.engine.clock.now()
    def on_announce_tcp_condrop(self):
        self.b_active = False
        self.t_last_heartbeat = None
    def at_turn(self, activity):
        if not self.b_active:
            return
        now = self.engine.clock.now()
        if now >= self.t_last_heartbeat+5:
            activity.mark(
                l=self,
                s='heartbeat_send')
            self.orb.nearcast(
                cog=self,
                message_h='heartbeat_send')
            self.t_last_heartbeat = now

def heartbeater_cog_new(cog_h, orb, engine):
    ob = HeartbeaterCog(
        cog_h=cog_h,
        orb=orb,
        engine=engine)
    return ob


