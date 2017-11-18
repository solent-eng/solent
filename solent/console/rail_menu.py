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
# // overview
# Provides an easy mechanism for managing a console-menu.

from collections import OrderedDict as od

from solent import ns

class RailMenu:
    def __init__(self):
        self.cs_menu_asks_display_to_clear = ns()
        self.cs_menu_asks_display_to_write = ns()
        self.cs_menu_selection = ns()
    def call_menu_selection(self, rail_h, keycode, text):
        self.cs_menu_selection.rail_h = rail_h
        self.cs_menu_selection.keycode = keycode
        self.cs_menu_selection.text = text
        self.cb_menu_selection(
            cs_menu_selection=self.cs_menu_selection)
    def call_menu_asks_display_to_clear(self, rail_h):
        self.cs_menu_asks_display_to_clear.rail_h = rail_h
        self.cb_menu_asks_display_to_clear(
            cs_menu_asks_display_to_clear=self.cs_menu_asks_display_to_clear)
    def call_menu_asks_display_to_write(self, rail_h, drop, rest, s):
        self.cs_menu_asks_display_to_write.rail_h = rail_h
        self.cs_menu_asks_display_to_write.drop = drop
        self.cs_menu_asks_display_to_write.rest = rest
        self.cs_menu_asks_display_to_write.s = s
        self.cb_menu_asks_display_to_write(
            cs_menu_asks_display_to_write=self.cs_menu_asks_display_to_write)

    def zero(self, rail_h, cb_menu_asks_display_to_clear, cb_menu_asks_display_to_write, cb_menu_selection, height, width, title):
        self.rail_h = rail_h
        self.cb_menu_asks_display_to_clear = cb_menu_asks_display_to_clear
        self.cb_menu_asks_display_to_write = cb_menu_asks_display_to_write
        self.height = height
        self.width = width
        self.title = title
        #
        self.d_menu = od()
    #
    def has_menu_keycode(self, menu_keycode):
        return menu_keycode in self.d_menu
    def add_menu_item(self, menu_keycode, text):
        if menu_keycode in self.d_menu:
            raise Exception('menu_keycode %s is already in menu')
        self.d_menu[menu_keycode] = text
    def select(self, menu_keycode):
        if menu_keycode not in self.d_menu:
            return
        text = self.d_menu[menu_keycode]
        self.call_menu_selection(
            rail_h=self.rail_h,
            keycode=menu_keycode,
            text=text)
    def render_menu(self):
        self.call_menu_asks_display_to_clear(
            rail_h=self.rail_h)
        self.call_menu_asks_display_to_write(
            rail_h=self.rail_h,
            drop=0,
            rest=0,
            s=self.title)
        for idx, (menu_keycode, text) in enumerate(self.d_menu.items()):
            self.call_menu_asks_display_to_write(
                rail_h=self.rail_h,
                drop=idx+2,
                rest=0,
                s="[%s] %s"%(chr(menu_keycode), text))
