#
# spin_menu
#
# // overview
# Provides an easy mechanism for managing a menu.
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

from solent.console import cgrid_new

from collections import OrderedDict as od

def menu_entry(text, cb_select):
    return (text, cb_select)

class SpinMenu:
    def __init__(self, height, width, cb_display_clear, cb_display_write):
        self.height = height
        self.width = width
        self.cb_display_clear = cb_display_clear
        self.cb_display_write = cb_display_write
        #
        self.title = ''
        self.cgrid = cgrid_new(
            width=width,
            height=height)
        self.d_menu = od()
    def set_title(self, text):
        self.title = text
    def has_menu_keycode(self, menu_keycode):
        return menu_keycode in self.d_menu
    def add_menu_item(self, menu_keycode, text, cb_select):
        '''
        cb_select() # no arguments
        '''
        if menu_keycode in self.d_menu:
            raise Exception('menu_keycode %s is already in menu')
        self.d_menu[menu_keycode] = menu_entry(
            text=text,
            cb_select=cb_select)
    def select(self, menu_keycode):
        if menu_keycode not in self.d_menu:
            return
        (text, cb_select) = self.d_menu[menu_keycode]
        cb_select()
    def render_menu(self):
        self.cb_display_clear()
        self.cb_display_write(
            drop=0,
            rest=0,
            s=self.title)
        for idx, (menu_keycode, tpl) in enumerate(self.d_menu.items()):
            (text, cb_select) = tpl
            self.cb_display_write(
                drop=idx+2,
                rest=0,
                s="[%s] %s"%(chr(menu_keycode), text))

def spin_menu_new(height, width, cb_display_clear, cb_display_write):
    '''
    cb_display_clear()
    cb_display_write(drop, rest, s)
    '''
    ob = SpinMenu(
        height=height,
        width=width,
        cb_display_clear=cb_display_clear,
        cb_display_write=cb_display_write)
    return ob

