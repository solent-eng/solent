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

class CsMenuAsksDisplayToClear:
    def __init__(self):
        self.menu_h = None

class CsMenuAsksDisplayToWrite:
    def __init__(self):
        self.menu_h = None
        self.drop = None
        self.rest = None
        self.s = None

class CsMenuSelection:
    def __init__(self):
        self.menu_h = None
        self.keycode = None

class RailMenu:
    def __init__(self):
        self.cs_menu_asks_display_to_clear = CsMenuAsksDisplayToClear()
        self.cs_menu_asks_display_to_write = CsMenuAsksDisplayToWrite()
        self.cs_menu_selection = CsMenuSelection()
    def zero(self, menu_h, cb_menu_asks_display_to_clear, cb_menu_asks_display_to_write, cb_menu_selection, height, width, title):
        self.menu_h = menu_h
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
        self._call_menu_selection(
            menu_h=self.menu_h,
            keycode=menu_keycode,
            text=text)
    def render_menu(self):
        self._call_menu_asks_display_to_clear(
            menu_h=self.menu_h)
        self._call_menu_asks_display_to_write(
            menu_h=self.menu_h,
            drop=0,
            rest=0,
            s=self.title)
        for idx, (menu_keycode, text) in enumerate(self.d_menu.items()):
            self._call_menu_asks_display_to_write(
                menu_h=self.menu_h,
                drop=idx+2,
                rest=0,
                s="[%s] %s"%(chr(menu_keycode), text))
    #
    def _call_menu_selection(self, menu_h, keycode, text):
        self.cs_menu_selection.menu_h = menu_h
        self.cs_menu_selection.keycode = keycode
        self.cs_menu_selection.text = text
        self.cb_menu_selection(
            cs_menu_selection=self.cs_menu_selection)
    def _call_menu_asks_display_to_clear(self, menu_h):
        self.cs_menu_asks_display_to_clear.menu_h = menu_h
        self.cb_menu_asks_display_to_clear(
            cs_menu_asks_display_to_clear=self.cs_menu_asks_display_to_clear)
    def _call_menu_asks_display_to_write(self, menu_h, drop, rest, s):
        self.cs_menu_asks_display_to_write.menu_h = menu_h
        self.cs_menu_asks_display_to_write.drop = drop
        self.cs_menu_asks_display_to_write.rest = rest
        self.cs_menu_asks_display_to_write.s = s
        self.cb_menu_asks_display_to_write(
            cs_menu_asks_display_to_write=self.cs_menu_asks_display_to_write)

