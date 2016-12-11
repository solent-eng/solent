#!/usr/bin/env python3
#
# gruel_client_sandbox
#
# // brief
# Draft terminal that can speak to a solent server. This is interesting
# because it shows use of the terminal in a nearcast context, as well as
# acting as a demonstration of a gruel client.
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

from solent import SolentQuitException
from solent.eng import engine_new
from solent.eng import nearcast_schema_new
from solent.eng import log_snoop_new
from solent.eng import nc_snoop_new
from solent.eng import orb_new
from solent.gruel import gruel_press_new
from solent.gruel import gruel_puff_new
from solent.gruel import gruel_schema_new
from solent.gruel import spin_gruel_client_new
from solent.log import init_logging
from solent.log import log
from solent.term import e_colpair
from solent.term import cgrid_new
from solent.util import line_finder_new

from collections import deque
from collections import OrderedDict as od
import random
import sys
import time
import traceback

# want this to work for people who do not have pygame installed
try:
    from solent.winterm import window_console_end as console_end
    from solent.winterm import window_console_start as console_start
except:
    from solent.term import curses_console_end as console_end
    from solent.term import curses_console_start as console_start
if '--tty' in sys.argv:
    from solent.term import curses_console_end as console_end
    from solent.term import curses_console_start as console_start

SERVER_ADDR = '127.0.0.1'
SERVER_PORT = 4100
SERVER_PASS = 'qweasd'

LCONSOLE_ADDR = '127.0.0.1'
LCONSOLE_PORT = 4091

TAP_ADDR = '127.0.0.1'
TAP_PORT = 4101

EVENT_ADDR = '127.0.0.1'
EVENT_PORT = 4102

I_NEARCAST_SCHEMA = '''
    i message h
    i field h

    message def_console
        field console
    
    message gruel_connect
        field server_ip
        field server_port
        field password

    message client_keystroke
        field u

    message term_announce
        field s

    message term_console_send_c
        field c

    message term_console_newline

    message term_console_backspace

    message term_plot
        field drop
        field rest
        field c
        field cpair
'''

KEY_ORD_BACKSPACE = 8
KEY_ORD_ENTER = 10
KEY_ORD_ESC = 27

class CogGruelClient:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.gruel_schema = gruel_schema_new()
        self.gruel_press = gruel_press_new(
            gruel_schema=self.gruel_schema,
            mtu=engine.mtu)
        self.gruel_puff = gruel_puff_new(
            gruel_schema=self.gruel_schema,
            mtu=engine.mtu)
        self.spin_gruel_client = spin_gruel_client_new(
            engine=engine,
            gruel_press=self.gruel_press,
            gruel_puff=self.gruel_puff)
    def at_turn(self, activity):
        "Returns a boolean which is True only if there was activity."
        self.spin_gruel_client.at_turn(
            activity=activity)
    def on_gruel_connect(self, server_ip, server_port, password):
        self.spin_gruel_client.attempt_connection(
            addr=server_ip,
            port=server_port,
            password=password,
            cb_connect=self._gruel_on_connect,
            cb_condrop=self._gruel_on_condrop,
            cb_doc=self._gruel_on_doc)
    #
    def on_send_something(self, text):
        pass
    #
    def _gruel_on_connect(self):
        self.orb.nearcast(
            cog_h=self.cog_h,
            message_h='term_announce',
            s='connected!')
    def _gruel_on_condrop(self, message):
        self.orb.nearcast(
            cog_h=self.cog_h,
            message_h='term_announce',
            s=message)
    def _gruel_on_doc(self, doc):
        log('got doc! [%s]'%doc)

class PanePlot:
    def __init__(self):
        self.pos = {}
    def plot(self, drop, rest, c, cpair):
        self.pos[ (drop, rest) ] = (c, cpair)
    def light(self, cgrid):
        for ((drop, rest), (c, cpair)) in self.pos.items():
            cgrid.put(
                drop=drop,
                rest=rest,
                s=c,
                cpair=cpair)

class PaneConsole:
    def __init__(self):
        self.buf = []
    def add(self, c):
        self.buf.append(c)
    def newline(self):
        self.buf = []
    def backspace(self):
        if self.buf:
            self.buf.pop()
    def light(self, cgrid):
        idx = 0
        for c in self.buf:
            drop = 1 + (idx / 40)
            rest = idx % 40
            cgrid.put(
                drop=drop,
                rest=rest,
                s=c,
                cpair=e_colpair.white_t)
            idx += 1
        drop = 1 + (idx / 40)
        rest = idx % 40
        cgrid.put(
            drop=drop,
            rest=rest,
            s='_',
            cpair=e_colpair.green_t)
        idx += 1
        while 0 != idx % 40:
            rest = idx % 40
            cgrid.put(
                drop=drop,
                rest=rest,
                s=' ',
                cpair=e_colpair.white_t)
            idx += 1
        cgrid.put(
            drop=drop+1,
            rest=0,
            s=' ',
            cpair=e_colpair.white_t)

class PaneAnnounce:
    def __init__(self):
        self.s = ''
    def set_text(self, s):
        self.s = s
    def light(self, cgrid):
        cgrid.put(
            drop=0,
            rest=0,
            s=self.s,
            cpair=e_colpair.red_t)
        cgrid.put(
            drop=0,
            rest=len(self.s),
            s=' '*(79-len(self.s)),
            cpair=e_colpair.red_t)

class CogTerminal:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.console = None
        self.cgrid = None
        self.pane_plot = None
        self.pane_console = None
        self.pane_announce = None
    #
    def at_turn(self, activity):
        k = self.console.async_getc()
        if k not in ('', None):
            activity.mark(
                l=self,
                s='key received')
            self.orb.nearcast(
                cog_h=self.cog_h,
                message_h='client_keystroke',
                u=k)
    def on_def_console(self, console):
        self.console = console
        self.cgrid = cgrid_new(
            width=console.width,
            height=console.height)
        self.pane_plot = PanePlot()
        self.pane_console = PaneConsole()
        self.pane_announce = PaneAnnounce()
    def on_client_keystroke(self, u):
        self.orb.nearcast(
            cog_h=self.cog_h,
            message_h='term_plot',
            drop=0,
            rest=79,
            c=u,
            cpair=e_colpair.yellow_t)
        self.orb.nearcast(
            cog_h=self.cog_h,
            message_h='term_plot',
            drop=1,
            rest=77,
            c='%3s'%(str(ord(u))),
            cpair=e_colpair.yellow_t)
        self._console_update()
    def on_term_announce(self, s):
        self.pane_announce.set_text(
            s=s)
        self._console_update()
    def on_term_console_send_c(self, c):
        self.pane_console.add(c)
        self._console_update()
    def on_term_console_newline(self):
        self.pane_console.newline()
        self._console_update()
    def on_term_console_backspace(self):
        self.pane_console.backspace()
        self._console_update()
    def on_term_plot(self, drop, rest, c, cpair):
        self.pane_plot.plot(
            drop=drop,
            rest=rest,
            c=c,
            cpair=cpair)
        self._console_update()
    #
    def _console_newline(self):
        self.tcurs_drop += 1
        self.tcurs_rest = 0
        if self.tcurs_drop >= 25:
            self.tcurs_drop = 0
    def _console_backspace(self):
        if self.tcurs_rest == 0:
            return
        self.tcurs_rest -= 1
        self.cgrid.put(
            drop=self.tcurs_drop,
            rest=self.tcurs_rest,
            s=' ',
            cpair=e_colpair.white_t)
        self._console_update()
    def _console_update(self):
        self.pane_plot.light(self.cgrid)
        self.pane_console.light(self.cgrid)
        self.pane_announce.light(self.cgrid)
        self.console.screen_update(
            cgrid=self.cgrid)

class CogShell:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.b_first = True
        self.line_finder = line_finder_new(
            cb_line=self._console_line)
    def at_turn(self, activity):
        if self.b_first:
            activity.mark(
                l=self,
                s='write quit message')
            self._console_announce(
                s='Press ESC to quit')
            self.b_first = False
    def on_client_keystroke(self, u):
        self.line_finder.accept_string(
            s=u)
        o = ord(u)
        if o == KEY_ORD_ENTER:
            self.orb.nearcast(
                cog_h=self.cog_h,
                message_h='term_console_newline')
        elif o == KEY_ORD_BACKSPACE:
            self.orb.nearcast(
                cog_h=self.cog_h,
                message_h='term_console_backspace')
        else:
            self.orb.nearcast(
                cog_h=self.cog_h,
                message_h='term_console_send_c',
                c=u)
    #
    def _console_announce(self, s):
        self.orb.nearcast(
            cog_h=self.cog_h,
            message_h='term_announce',
            s=s)
    def _console_line(self, line):
        if line == 'start':
            self.orb.nearcast(
                cog_h=self.cog_h,
                message_h='gruel_connect',
                server_ip=SERVER_ADDR,
                server_port=SERVER_PORT,
                password=SERVER_PASS)
        else:
            self._console_announce(
                s='syntax error')

class CogPlotRandomness:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.t = time.time()
    def at_turn(self, activity):
        now = time.time()
        if now - 1 > self.t:
            activity.mark(
                l=self,
                s='sending a random char')
            self._send_a_random_char()
            self.t = now
    #
    def _send_a_random_char(self):
        drop = random.choice(range(25))
        rest = random.choice(range(60, 80))
        c = chr(random.choice(range(ord('a'), ord('z')+1)))
        cpair = random.choice([e for e in e_colpair if not e.name.startswith('_')])
        self.orb.nearcast(
            cog_h=self.cog_h,
            message_h='term_plot',
            drop=drop,
            rest=rest,
            c=c,
            cpair=cpair)

class CogQuitScanner:
    # Looks out for a particular letter, and tells the app to quit when it
    # sees it.
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.b_first = True
    def on_client_keystroke(self, u):
        if ord(u) == KEY_ORD_ESC:
            raise SolentQuitException()

def wrap_eng(console):
    init_logging()
    engine = engine_new(
        mtu=1500)
    engine.default_timeout = 0.02
    try:
        nearcast_schema = nearcast_schema_new(
            i_nearcast=I_NEARCAST_SCHEMA)
        # snoop = nc_snoop_new(
        #     engine=engine,
        #     nearcast_schema=nearcast_schema,
        #     addr=TAP_ADDR,
        #     port=TAP_PORT)
        # snoop = log_snoop_new(
        #     nearcast_schema=nearcast_schema)
        orb = engine.init_orb(
            nearcast_schema=nearcast_schema)
            #snoop=snoop)
        #
        orb.init_cog(CogGruelClient)
        orb.init_cog(CogShell)
        orb.init_cog(CogTerminal)
        #orb.init_cog(CogPlotRandomness)
        orb.init_cog(CogQuitScanner)
        #
        orb.nearcast(
            cog_h='prep',
            message_h='def_console',
            console=console)
        #
        engine.event_loop()
    except KeyboardInterrupt:
        pass
    except SolentQuitException:
        pass
    except:
        traceback.print_exc()
    finally:
        engine.close()

def main():
    try:
        console = console_start(
            width=80,
            height=25)

        wrap_eng(
            console=console)
    except:
        traceback.print_exc()
    finally:
        console_end()

if __name__ == '__main__':
    main()

