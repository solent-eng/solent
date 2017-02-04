#
# console_demo
#
# // overview
# created to demonstrate simple uses cases of the console, including
# asynchronous interaction.
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

from solent import solent_cpair
from solent import solent_cpair_pairs
from solent import solent_keycode
from solent import uniq
from solent.console import cgrid_new
from solent.console import console_new
from solent.exceptions import SolentQuitException

import sys
import time
import traceback

ESC_KEY_ORD = 27

C_GAME_WIDTH = 78
C_GAME_HEIGHT = 25

def event_loop(console):
    cgrid = cgrid_new(
        width=console.width,
        height=console.height)
    cgrid.put(
        drop=console.height-3,
        rest=1,
        s='(Escape to quit)',
        cpair=solent_cpair('white'))
    for (idx, (cpair, name)) in enumerate(solent_cpair_pairs()):
        cgrid.put(
            drop=(5+int(idx/4)),
            rest=(2+int(18*(idx%4))),
            s='%s %s'%(name, cpair),
            cpair=cpair)
    console.screen_update(
        cgrid=cgrid)
    #
    t = 0
    while True:
        keycode = console.async_get_keycode()
        if keycode != None:
            if keycode == solent_keycode('esc'):
                raise SolentQuitException()
            cgrid.put(
                drop=3,
                rest=1,
                s='key %s (%s)  '%(hex(keycode), chr(keycode)),
                cpair=solent_cpair('red'))
        else:
            time.sleep(0.05)
        cgrid.put(
            drop=1,
            rest=1,
            s='loop counter: %s'%(t),
            cpair=solent_cpair('green'))
        console.screen_update(
            cgrid=cgrid)
        t += 1

def main():
    if '--pygame' in sys.argv:
        console_type = 'pygame'
    elif '--curses' in sys.argv:
        console_type = 'curses'
    else:
        print('ERROR: specify --curses or --pygame')
        sys.exit(1)
    #
    console = None
    try:
        console = console_new(
            console_type=console_type,
            width=C_GAME_WIDTH,
            height=C_GAME_HEIGHT)
        event_loop(
            console=console)
    except SolentQuitException:
        pass
    except:
        traceback.print_exc()
    finally:
        if None != console:
            console.close()
    
if __name__ == '__main__':
    main()

