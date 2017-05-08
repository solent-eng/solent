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
#
# // Overview
# Here, we introduce the concepts of nearcast, orb, and cog.
#
# In the main function, we instantiate an orb. We use a domain-specific
# language to do this, as seen in I_NEARCAST. In the usage below, I_NEARCAST
# defines a single message vector, 'nearcast_note' containg two fields.
#
# Next, we initialise instances of each of the cogs. When they are
# initialised they are attached (subscribed) to the nearcast for the
# messages that they have on_blah methods for.
# 
# The cogs use nearcast vectors to communicate between one another.
# 
# CogSender will be instantiated. As the event loop runs, CogSender receives
# initiative from the orb (orb calls orb_turn). The instance of CogSender will
# count turns of the event loop. On turn #3 it nearcasts.
#
# CogPrint has a method that watches for messages of type nearcast_note, and
# then prints them out. This demonstrates the special role of 'on_blah'. Such
# methods subscribe to the nearcast.
# 
# CogQuitter counts turns, and quits a while longer than the other activity.

from solent import SolentQuitException
from solent.eng import engine_new
from solent.log import log

MTU = 1400

I_NEARCAST = '''
    i message h
    i field h

    message nearcast_note
        field field_a
        field field_b
'''

class CogSender:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.turn_counter = 0
    def orb_turn(self, activity):
        self.turn_counter += 1
        if self.turn_counter == 3:
            activity.mark(
                l=self,
                s="reached the important turn")
            #
            # The next line uses a convenience object that is injected
            # into the cog when the orb initialises it. Internally, this
            # is what it is doing:
            # 
            #   self.orb.nearcast(
            #       cog=self,
            #       message_h='nearcast_note',
            #       field_a='text in a',
            #       field_b='text in b')
            #
            # So why this unusual code injection rather than asking the user
            # to write the code above? Writing to the nearcast is a frequent
            # operation. The usage below is faster and less distracting once
            # you are fluent.
            #
            self.nearcast.nearcast_note(
                field_a='text in a',
                field_b='text in b')
            log('%s sent nearcast note'%(self.cog_h))

class CogPrinter:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
    def on_nearcast_note(self, field_a, field_b):
        log('%s received nearcast_note [%s] [%s]'%(
            self.cog_h, field_a, field_b))

class CogQuitter:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.turn_counter = 0
    def orb_turn(self, activity):
        self.turn_counter += 1
        if self.turn_counter == 8:
            activity.mark(
                l=self,
                s='last turn, quitting')
            log('quitting')
            raise SolentQuitException()

def app():
    engine = engine_new(
        mtu=MTU)
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST)
    #
    orb.init_cog(CogSender)
    orb.init_cog(CogPrinter)
    orb.init_cog(CogQuitter)
    #
    engine.event_loop()

def main():
    try:
        app()
    except KeyboardInterrupt:
        pass
    except SolentQuitException:
        pass

if __name__ == '__main__':
    main()

