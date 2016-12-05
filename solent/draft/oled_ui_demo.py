#!/usr/bin/env python3
#
# oled user interface demo
#
# // overview
# Some new laptops ship with 'OLED' screens. They differ from the screens of
# the previous generation in that they only send power to pixels that need
# them. This gives incentive to create a user interface based on a minimal
# display of pixels. This demo plays with that idea.
#
# To use this demonstration, run app. This shows the window perimeters. Press
# enter, and it shows the same screen without the window perimeters.
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

import os
import sys


# --------------------------------------------------------
#   :console_display
# --------------------------------------------------------
class bcol:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDER = '\033[4m'
    BLINK = '\033[5m'
    REV = '\033[7m'
    INVIS = '\033[8m'
    #
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    WHITE = '\033[37m'
    #
    BG_BLACK = '\033[40m'
    BG_DEFAULT = '\033[49m'

def pause(b_show_paused_message=True):
    if b_show_paused_message:
        print('[paused]')
    input()

def colour_test():
    print("%s%s%s"%(bcol.BLACK, 'bcol.BLACK', bcol.RESET))
    print("%s%s%s%s"%(bcol.BOLD, bcol.BLACK, 'bcol.BLACK bold', bcol.RESET))
    print("%s%s%s%s"%(bcol.DIM, bcol.BLACK, 'bcol.BLACK dim', bcol.RESET))
    print("%s%s%s%s"%(bcol.UNDER, bcol.BLACK, 'bcol.BLACK UNDER', bcol.RESET))
    print("%s%s%s%s"%(bcol.REV, bcol.BLACK, 'bcol.BLACK REV', bcol.RESET))
    print("%s%s%s%s"%(bcol.INVIS, bcol.BLACK, 'bcol.BLACK INVIS', bcol.RESET))
    #
    print("%s%s%s"%(bcol.RED, 'bcol.RED', bcol.RESET))
    print("%s%s%s%s"%(bcol.BOLD, bcol.RED, 'bcol.RED bold', bcol.RESET))
    print("%s%s%s%s"%(bcol.DIM, bcol.RED, 'bcol.RED dim', bcol.RESET))
    print("%s%s%s%s"%(bcol.UNDER, bcol.RED, 'bcol.RED UNDER', bcol.RESET))
    print("%s%s%s%s"%(bcol.REV, bcol.RED, 'bcol.RED REV', bcol.RESET))
    print("%s%s%s%s"%(bcol.INVIS, bcol.RED, 'bcol.RED INVIS', bcol.RESET))
    #
    print(''.join([bcol.BG_DEFAULT, bcol.RED, 'bg def bcol.RED', bcol.RESET]))
    print(''.join([bcol.BG_BLACK, bcol.RED, 'bg black bcol.RED', bcol.RESET]))
    #
    print("%s%s%s"%(bcol.GREEN, 'bcol.GREEN', bcol.RESET))
    print("%s%s%s%s"%(bcol.BOLD, bcol.GREEN, 'bcol.GREEN bold', bcol.RESET))
    print("%s%s%s"%(bcol.YELLOW, 'bcol.YELLOW', bcol.RESET))
    print("%s%s%s%s"%(bcol.BOLD, bcol.YELLOW, 'bcol.YELLOW bold', bcol.RESET))
    print("%s%s%s"%(bcol.BLUE, 'bcol.BLUE', bcol.RESET))
    print("%s%s%s%s"%(bcol.BOLD, bcol.BLUE, 'bcol.BLUE bold', bcol.RESET))
    print("%s%s%s"%(bcol.PURPLE, 'bcol.PURPLE', bcol.RESET))
    print("%s%s%s%s"%(bcol.BOLD, bcol.PURPLE, 'bcol.PURPLE bold', bcol.RESET))
    print("%s%s%s"%(bcol.WHITE, 'bcol.WHITE', bcol.RESET))
    print("%s%s%s%s"%(bcol.BOLD, bcol.WHITE, 'bcol.WHITE bold', bcol.RESET))
    print("%s%s%s"%(bcol.UNDERLINE, 'bcol.UNDERLINE', bcol.RESET))


# --------------------------------------------------------
#   :sigils
# --------------------------------------------------------
C_APARATUS = (bcol.BOLD, bcol.BLUE)
C_BARRIER = (bcol.BOLD, bcol.PURPLE)
C_BUFFER_BOLD = (bcol.BOLD, bcol.GREEN)
C_BUFFER_DIM = (bcol.DIM, bcol.GREEN)
C_BUTTON = (bcol.BOLD, bcol.PURPLE)
C_CORPSE = (bcol.DIM, bcol.RED)
C_FEATURES = (bcol.DIM, bcol.BLACK)
C_HELP = (bcol.BOLD, bcol.BLUE)
C_KEYBOARD = (bcol.DIM, bcol.BLUE)
C_LEAFY = (bcol.DIM, bcol.GREEN)
C_LOCATION = (bcol.DIM, bcol.GREEN)
C_NOISE = (bcol.BOLD, bcol.WHITE)
C_OPERATOR = (bcol.BOLD, bcol.GREEN)
C_PATTERNS = (bcol.DIM, bcol.GREEN)
C_PLAYER = (bcol.BOLD, bcol.GREEN)
C_PROMPT_ACTIVE = (bcol.DIM, bcol.GREEN, bcol.BLINK)
C_PROMPT_PASSIVE = (bcol.DIM, bcol.BLACK)
C_QUIT_TEXT = (bcol.DIM, bcol.BLUE)
C_RESOURCES = (bcol.BOLD, bcol.BLACK)
C_ROBOTICS = (bcol.BOLD, bcol.RED)
C_SENTIENCE = (bcol.BOLD, bcol.YELLOW)
C_SIDEBAR_CONTROLS = (bcol.BOLD, bcol.GREEN)
C_STATUS = (bcol.DIM, bcol.BLUE)
C_WINDOW_CONTROLS = (bcol.BOLD, bcol.YELLOW)




# --------------------------------------------------------
#   :vox
# --------------------------------------------------------
class Vox(object):
    def __init__(self, s, e, c, *properties):
        self.s = s
        self.e = e
        self.c = c
        self.properties = properties
    def __repr__(self):
        l = []
        for itm in self.properties:
            l.append(itm)
        l.append(self.c)
        l.append(bcol.RESET)
        return '%s%s%s'%(''.join(self.properties), self.c, bcol.RESET)


# --------------------------------------------------------
#   :display
# --------------------------------------------------------
class Window(object):
    def __init__(self, screen, code, title, s, e, drop, rest, cb_get_scene):
        self.screen = screen
        self.code = code
        self.title = title
        self.s = s
        self.e = e
        self.rest = rest
        self.drop = drop
        # fn(drop, rest) -> [Vox]
        self.cb_get_scene = cb_get_scene
        #
        self.is_visible = False
    def hide(self):
        self.is_visible = False
        return self
    def show(self):
        self.is_visible = True
        return self

class Screen(object):
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.windows = []
        self.b_show_window_controls = True
    def create_window(self, code, title, s, e, drop, rest, cb_get_scene):
        w = Window(
            screen=self,
            code=code,
            title=title,
            s=s,
            e=e,
            drop=drop,
            rest=rest,
            cb_get_scene=cb_get_scene)
        self.windows.append(w)
        return w
    def render(self):
        os.system('clear')
        #
        # this is where we will buffer all the voxes we need to
        # account for.
        vlist = []
        def v(s, e, c, *props):
            vlist.append( Vox(s, e, c, *props) )
        #
        # populate our windows
        for w in self.windows[::-1]:
            if not w.is_visible:
                continue
            for vox in w.cb_get_scene(w.s, w.e, w.drop-2, w.rest-2):
                vlist.append(vox)
        #
        # window controls
        if self.b_show_window_controls:
            # render windows from the last to the first
            for w in self.windows[::-1]:
                if not w.is_visible:
                    continue
                topleft = '%s %s'%(w.title, '-'*(w.rest-len(w.title)-3))
                for i, c in enumerate(topleft):
                    v(w.s, w.e+i, c, *C_WINDOW_CONTROLS)
                v(w.s, w.e+w.rest-1, 'x', *C_WINDOW_CONTROLS)
                v(w.s+w.drop, w.e, '=', *C_WINDOW_CONTROLS)
                for i in range(w.rest - 4):
                    v(w.s+w.drop, w.e+2+i, '-', *C_WINDOW_CONTROLS)
                v(w.s+w.drop, w.e+w.rest-1, 'o', *C_WINDOW_CONTROLS)
        #
        # place sidebar
        sidebar = []
        for w in self.windows:
            sidebar.append(w.code)
        sidebar.append('.')
        for i, c in enumerate(sidebar):
            v(i*2, self.width-1, c, *C_SIDEBAR_CONTROLS)
        #
        # create an empty buffer
        buf = []
        for drop in range(self.height):
            cols = []
            for rest in range(self.width):
                cols.append(' ')
            buf.append(cols)
        #
        # place the voxes into the buffer
        for vox in vlist:
            buf[vox.s][vox.e] = str(vox)
        #
        # output
        for r in buf:
            print(''.join(r))


# --------------------------------------------------------
#   :grid
# --------------------------------------------------------
def grid_barrier_dots(s, e, drop, rest):
    return [
        Vox(s+0, e+0, '.', *C_BARRIER),
        Vox(s+0, e+rest, '.', *C_BARRIER),
        Vox(s+drop, e+0, '.', *C_BARRIER),
        Vox(s+drop, e+rest, '.', *C_BARRIER)]

def grid_leafy(s, e, drop, rest):
    return [
         Vox(s+0,  e+1,  'l', *C_LEAFY),
         Vox(s+0,  e+2,  'l', *C_LEAFY),
         Vox(s+0,  e+3,  'f', *C_LEAFY),
         Vox(s+1,  e+1,  'l', *C_LEAFY),
         Vox(s+1,  e+2,  'l', *C_LEAFY),
         Vox(s+1,  e+3,  's', *C_LEAFY)]

def grid_features(s, e, drop, rest):
    return [
        Vox(s+5,  e+12, '|', *C_FEATURES),
        Vox(s+7,  e+12, 'o', *C_FEATURES),
        Vox(s+4,  e+13, '-', *C_FEATURES),
        Vox(s+4,  e+14, '-', *C_FEATURES),
        Vox(s+4,  e+15, '-', *C_FEATURES),
        Vox(s+4,  e+17, '-', *C_FEATURES),
        Vox(s+4,  e+18, '-', *C_FEATURES),
        Vox(s+4,  e+19, 'o', *C_FEATURES),
        Vox(s+6,  e+15, '@', *C_PLAYER),
        Vox(s+6,  e+19, '.', *C_RESOURCES),
        Vox(s+6,  e+20, '%', *C_RESOURCES)]

def cb_grid(s, e, drop, rest):
    s+=1
    #
    l = []
    s+=6
    e+=12
    l.extend(grid_leafy(s, e, drop, rest))
    l.extend(grid_features(s, e, drop, rest))
    #
    # sentience and robotics
    l.extend([
        Vox(s+6,  e+17, '@', *C_SENTIENCE),
        Vox(s+8,  e+20, 'n', *C_SENTIENCE),
        Vox(s+8,  e+21, 's', *C_SENTIENCE),
        Vox(s+10, e+18, '%', *C_CORPSE),
        Vox(s+8,  e+2,  '"', *C_ROBOTICS)])
    #
    # speech
    l.extend([
        Vox(s+5,  e+18, 'g',  *C_NOISE),
        Vox(s+5,  e+19, 'r',  *C_NOISE),
        Vox(s+5,  e+20, 'e',  *C_NOISE),
        Vox(s+5,  e+21, 'e',  *C_NOISE),
        Vox(s+5,  e+22, 't',  *C_NOISE),
        Vox(s+5,  e+23, 'i',  *C_NOISE),
        Vox(s+5,  e+24, 'n',  *C_NOISE),
        Vox(s+5,  e+25, 'g',  *C_NOISE),
        Vox(s+5,  e+26, 's',  *C_NOISE)])
    #
    # aparatus
    l.extend([
        Vox(s+10, e+7,  'u', *C_APARATUS),
        Vox(s+10, e+8,  '-', *C_APARATUS),
        Vox(s+10, e+9,  '-', *C_APARATUS),
        Vox(s+9,  e+10, '&', *C_APARATUS),
        Vox(s+10, e+10, '+', *C_APARATUS),
        Vox(s+11, e+10, '|', *C_APARATUS),
        Vox(s+12, e+10, 'f', *C_APARATUS),
        Vox(s+10, e+11, '-', *C_APARATUS),
        Vox(s+10, e+12, 'u', *C_APARATUS)])
    #
    return l



# --------------------------------------------------------
#   :alg
# --------------------------------------------------------
DISPLAY_WIDTH = 78
DISPLAY_HEIGHT = 44

def cb_quit(s, e, drop, rest):
    s+=1
    l = []
    for (idx, c) in enumerate('really quit?'):
        l.append(Vox(s+0, e+idx, c, *C_QUIT_TEXT))
    for (idx, c) in enumerate('yes'):
        l.append(Vox(s+2, e+idx, c, *C_BUTTON))
    for (idx, c) in enumerate('no'):
        l.append(Vox(s+3, e+idx, c, *C_BUTTON))
    return l

def cb_help(s, e, drop, rest):
    s+=1
    l = []
    l.append(Vox(s+4, e+5, '?', *C_HELP))
    return l

def cb_status(s, e, drop, rest):
    s+=1
    notes = [
        '@ august',
        'n unknown',
        's unknown']
    l = []
    for (ridx, n) in enumerate(notes):
        col = C_STATUS
        for (cidx, c) in enumerate(n):
            l.append(Vox(s+ridx, e+cidx, c, *col))
    
    return l

def cb_buffer(s, e, drop, rest):
    s+=1
    l = []
    for (idx, c) in enumerate("why are you so hysterical"):
        ss = s + drop - 1
        ee = e + idx
        l.append(Vox(ss, ee, c, *C_BUFFER_DIM))
    for (idx, c) in enumerate("you are tearing me apart, lisa"):
        ss = s + drop
        ee = e + idx
        l.append(Vox(ss, ee, c, *C_BUFFER_BOLD))
    return l

def cb_prompt(s, e, drop, rest):
    s+=1
    l = [ Vox(s+0, e+0, '#', *C_OPERATOR)
        , Vox(s+0, e+2, '_', *C_PROMPT_PASSIVE)
        ]
    return l

KEYBOARD = '''
    1   2   3   4   5   6   7   8   9   0   <

     q   w   e   r   t   y   u   i   o   p

      a   s   d   f   g   h   j   k   l

        z   x   c   v   b   n   m   ,   .
'''

def cb_keys(s, e, drop, rest):
    s+=1
    l = []
    for (ridx, r) in enumerate(KEYBOARD.split('\n')):
        for (cidx, c) in enumerate(r):
            if c != ' ':
                l.append(Vox(s+ridx, e+cidx, c, *C_KEYBOARD))
    return l

def cb_patterns(s, e, drop, rest):
    s+=1
    macros = [ 'nw nn ne   #hold   #take'
             , 'ww    ee   #stow   #drop'
             , 'sw ss se   #desc   #cook'
             ]
    l = []
    for (ridx, mstr) in enumerate(macros):
        for (cidx, c) in enumerate(mstr):
            l.append(Vox(s+(2*ridx), e+cidx, c, *C_PATTERNS))
    return l

def main():
    screen = Screen(DISPLAY_HEIGHT, DISPLAY_WIDTH)
    screen.create_window(
        code='x',
        title='quit',
        s=0,
        e=0,
        drop=6,
        rest=27,
        cb_get_scene=cb_quit).hide()
    screen.create_window(
        code='?',
        title='help',
        s=10,
        e=10,
        drop=11,
        rest=11,
        cb_get_scene=cb_help).show()
    screen.create_window(
        code='k',
        title='keys',
        s=DISPLAY_HEIGHT-1-10,
        e=30,
        drop=10,
        rest=48,
        cb_get_scene=cb_keys).hide()
    screen.create_window(
        code='p',
        title='patterns',
        s=37,
        e=45,
        drop=6,
        rest=32,
        cb_get_scene=cb_patterns).hide()
    screen.create_window(
        code='g',
        title='grid',
        s=10,
        e=13,
        drop=29,
        rest=52,
        cb_get_scene=cb_grid).show()
    screen.create_window(
        code='s',
        title='status',
        s=0,
        e=43,
        drop=10,
        rest=34,
        cb_get_scene=cb_status).show()
    screen.create_window(
        code='b',
        title='buffer',
        s=DISPLAY_HEIGHT-16,
        e=0,
        drop=15,
        rest=45,
        cb_get_scene=cb_buffer).hide()
    screen.create_window(
        code='#',
        title='prompt',
        s=0,
        e=0,
        drop=25,
        rest=44,
        cb_get_scene=cb_prompt).show()
    screen.b_show_window_controls = True
    screen.render()
    pause(False)
    screen.b_show_window_controls = False
    screen.render()
    pause(False)

if __name__ == '__main__':
    if '--test' in sys.argv:
        colour_test()
    main()

