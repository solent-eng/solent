#
# basic_term_demo
#
# // overview
# created to demonstrate async functionality
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

from solent.term import e_colpair
from solent.term import cgrid_new
from solent.term import curses_console_start
from solent.term import curses_console_end
from solent.winterm import window_console_start
from solent.winterm import window_console_end
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
        cpair=e_colpair.white_t)
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
                    cpair=e_colpair.red_t)
        else:
            time.sleep(0.05)
        cgrid.put(
            drop=1,
            rest=1,
            s='loop counter: %s'%(t),
            cpair=e_colpair.green_t)
        console.screen_update(
            cgrid=cgrid)
        t += 1

def main():
    if '--tty' in sys.argv:
        fn_device_start = curses_console_start
        fn_device_end = curses_console_end
    elif '--win' in sys.argv:
        fn_device_start = window_console_start
        fn_device_end = window_console_end
    else:
        print('ERROR: specify --tty or --win')
        sys.exit(1)
    try:
        console = fn_device_start(
            width=C_GAME_WIDTH,
            height=C_GAME_HEIGHT)
        event_loop(
            console=console)
    except SolentQuitException:
        pass
    except:
        traceback.print_exc()
    finally:
        fn_device_end()
    
if __name__ == '__main__':
    main()

