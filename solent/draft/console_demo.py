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

from solent import e_cpair
from solent.console import cgrid_new
from solent.console import console_new
from solent.exceptions import SolentQuitException
from solent.util import uniq

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
        cpair=e_cpair.white_t)
    console.screen_update(
        cgrid=cgrid)
    #
    t = 0
    while True:
        k = console.async_getc()
        if k != None:
            for idx, k in enumerate(k):
                if len(k) == 0:
                    continue
                if ord(k) == ESC_KEY_ORD:
                    raise SolentQuitException()
                cgrid.put(
                    drop=3+idx,
                    rest=1,
                    s='key %s (%s)  '%(str(k), ord(k)),
                    cpair=e_cpair.red_t)
        else:
            time.sleep(0.05)
        cgrid.put(
            drop=1,
            rest=1,
            s='loop counter: %s'%(t),
            cpair=e_cpair.green_t)
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

