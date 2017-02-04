#
# action_pool
#
# // overview
# Object pool wrapping actions, a class of object designed to be used by the
# engine for controlling the initiative in its event loop.
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

class Action:
    def __init__(self):
        #
        self.tmil = None
        self.fn_ask = None
        self.fn_turn = None
        self.b_recurring = None
    def set(self, tmil, fn_ask, fn_turn, b_recurring):
        self.tmil = tmil
        self.fn_ask = fn_ask
        self.fn_turn = fn_turn
        self.b_recurring = b_recurring

class ActionPool:
    def __init__(self):
        self.stack = []
    def push(self, action):
        self.stack.append(action)
    def pull(self, tmil, fn_ask, fn_turn, b_recurring):
        if 0 == len(self.stack):
            self.stack.append(Action())
        action = self.stack.pop()
        action.set(
            tmil=tmil,
            fn_ask=fn_ask,
            fn_turn=fn_turn,
            b_recurring=b_recurring)
        return action

def action_pool_new():
    ob = ActionPool()
    return ob

