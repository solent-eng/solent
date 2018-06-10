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

from solent import Ns
from solent import pool_rail_class

class RailAlarmBooking:
    def zero(self, rail_h, cb_alarm_event, value, at_t):
        self.rail_h = rail_h
        self.cb_alarm_event = cb_alarm_event
        self.value = value
        self.at_t = at_t

class SpinRoughAlarm:
    # In issues #119 and #121 we will be implementing various alarms in the
    # engine. Here, I make no claim to do a good job of this. But I need an
    # alarm
    def __init__(self, spin_h, engine):
        self.spin_h = spin_h
        self.engine = engine
        #
        self.cs_alarm_event = Ns()
        #
        self.pool_alarm_booking = pool_rail_class(RailAlarmBooking)
        self.work = []
        self.buffer = []
    def call_alarm_event(self, cb_alarm_event, zero_h, value, at_t):
        self.cs_alarm_event.zero_h = zero_h
        self.cs_alarm_event.value = value
        self.cs_alarm_event.at_t = at_t
        cb_alarm_event(
            cs_alarm_event=self.cs_alarm_event)
    def eng_turn(self, activity):
        now = self.engine.clock.now()
        #
        self.buffer.clear()
        for (idx, rail_alarm_booking) in enumerate(self.work):
            if rail_alarm_booking.at_t <= now:
                self.buffer.append(idx)
        #
        idx_reduce = 0
        for original_idx in self.buffer:
            idx = original_idx - idx_reduce
            idx_reduce += 1
            #
            rail_alarm_booking = self.work[idx]
            self.call_alarm_event(
                cb_alarm_event=rail_alarm_booking.cb_alarm_event,
                zero_h=self.spin_h,
                value=rail_alarm_booking.value,
                at_t=rail_alarm_booking.at_t)
            del self.work[idx]
            self.pool_alarm_booking.put(rail_alarm_booking)
    def eng_close(self):
        pass
    def book_time(self, cb_alarm_event, value, at_t):
        rail_h = '%s/alarm_booking'%(self.spin_h)
        rail_alarm_booking = self.pool_alarm_booking.get(
            rail_h=rail_h,
            cb_alarm_event=cb_alarm_event,
            value=value,
            at_t=at_t)
        self.work.append(rail_alarm_booking)

