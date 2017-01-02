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
from solent.eng import orb_new
from solent.gruel import gruel_press_new
from solent.gruel import gruel_puff_new
from solent.gruel import gruel_schema_new
from solent.gruel import spin_gruel_client_new
from solent.log import init_logging
from solent.log import log
from solent.console import e_colpair
from solent.console import cgrid_new
from solent.util import line_finder_new

from collections import deque
from collections import OrderedDict as od
import random
import sys
import time
import traceback

# want this to work for people who do not have pygame installed
if '--tty' in sys.argv:
    from solent.console import curses_console_new as console_new
else:
    try:
        from solent.winconsole import window_console_new as console_new
    except:
        from solent.console import curses_console_new as console_new

I_NEARCAST_SCHEMA = '''
    i message h
    i field h

    message def_console
        field console
    
    message instruct_gruel_connect
        field server_ip
        field server_port
        field password

    message instruct_gruel_condrop

    message instruct_gruel_send
        field doc

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

FACES_IN_THE_STREET = '''
.-------------------------------------------------------
They lie, the men who tell us in a loud decisive tone 
That want is here a stranger, and that misery's unknown; 
For where the nearest suburb and the city proper meet 
My window-sill is level with the faces in the street -- 
Drifting past, drifting past, 
To the beat of weary feet -- 
While I sorrow for the owners of those faces in the street. 

And cause I have to sorrow, in a land so young and fair, 
To see upon those faces stamped the marks of Want and Care; 
I look in vain for traces of the fresh and fair and sweet 
In sallow, sunken faces that are drifting through the street -- 
Drifting on, drifting on, 
To the scrape of restless feet; 
I can sorrow for the owners of the faces in the street. 

In hours before the dawning dims the starlight in the sky 
The wan and weary faces first begin to trickle by, 
Increasing as the moments hurry on with morning feet, 
Till like a pallid river flow the faces in the street -- 
Flowing in, flowing in, 
To the beat of hurried feet -- 
Ah! I sorrow for the owners of those faces in the street. 

The human river dwindles when 'tis past the hour of eight, 
Its waves go flowing faster in the fear of being late; 
But slowly drag the moments, whilst beneath the dust and heat 
The city grinds the owners of the faces in the street -- 
Grinding body, grinding soul, 
Yielding scarce enough to eat -- 
Oh! I sorrow for the owners of the faces in the street. 

And then the only faces till the sun is sinking down 
Are those of outside toilers and the idlers of the town, 
Save here and there a face that seems a stranger in the street, 
Tells of the city's unemployed upon his weary beat -- 
Drifting round, drifting round, 
To the tread of listless feet -- 
Ah! My heart aches for the owner of that sad face in the street. 

And when the hours on lagging feet have slowly dragged away, 
And sickly yellow gaslights rise to mock the going day, 
Then flowing past my window like a tide in its retreat, 
Again I see the pallid stream of faces in the street -- 
Ebbing out, ebbing out, 
To the drag of tired feet, 
While my heart is aching dumbly for the faces in the street. 

And now all blurred and smirched with vice the day's sad pages end, 
For while the short `large hours' toward the longer `small hours' trend, 
With smiles that mock the wearer, and with words that half entreat, 
Delilah pleads for custom at the corner of the street -- 
Sinking down, sinking down, 
Battered wreck by tempests beat -- 
A dreadful, thankless trade is hers, that Woman of the Street. 

But, ah! to dreader things than these our fair young city comes, 
For in its heart are growing thick the filthy dens and slums, 
Where human forms shall rot away in sties for swine unmeet, 
And ghostly faces shall be seen unfit for any street -- 
Rotting out, rotting out, 
For the lack of air and meat -- 
In dens of vice and horror that are hidden from the street. 

I wonder would the apathy of wealthy men endure 
Were all their windows level with the faces of the Poor? 
Ah! Mammon's slaves, your knees shall knock, your hearts in terror beat, 
When God demands a reason for the sorrows of the street, 
The wrong things and the bad things 
And the sad things that we meet 
In the filthy lane and alley, and the cruel, heartless street. 

I left the dreadful corner where the steps are never still, 
And sought another window overlooking gorge and hill; 
But when the night came dreary with the driving rain and sleet, 
They haunted me -- the shadows of those faces in the street, 
Flitting by, flitting by, 
Flitting by with noiseless feet, 
And with cheeks but little paler than the real ones in the street. 

Once I cried: `Oh, God Almighty! if Thy might doth still endure, 
Now show me in a vision for the wrongs of Earth a cure.' 
And, lo! with shops all shuttered I beheld a city's street, 
And in the warning distance heard the tramp of many feet, 
Coming near, coming near, 
To a drum's dull distant beat, 
And soon I saw the army that was marching down the street. 

Then, like a swollen river that has broken bank and wall, 
The human flood came pouring with the red flags over all, 
And kindled eyes all blazing bright with revolution's heat, 
And flashing swords reflecting rigid faces in the street. 
Pouring on, pouring on, 
To a drum's loud threatening beat, 
And the war-hymns and the cheering of the people in the street. 

And so it must be while the world goes rolling round its course, 
The warning pen shall write in vain, the warning voice grow hoarse, 
But not until a city feels Red Revolution's feet 
Shall its sad people miss awhile the terrors of the street -- 
The dreadful everlasting strife 
For scarcely clothes and meat 
In that pent track of living death -- the city's cruel street. 
--------------------------------------------------------.'''

SERVER_ADDR = '127.0.0.1'
SERVER_PORT = 4100
SERVER_PASS = 'qweasd'

LCONSOLE_ADDR = '127.0.0.1'
LCONSOLE_PORT = 4091

TAP_ADDR = '127.0.0.1'
TAP_PORT = 4101

EVENT_ADDR = '127.0.0.1'
EVENT_PORT = 4102

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
    def on_instruct_gruel_connect(self, server_ip, server_port, password):
        self.spin_gruel_client.order_connect(
            addr=server_ip,
            port=server_port,
            password=password,
            cb_connect=self._gruel_on_connect,
            cb_condrop=self._gruel_on_condrop,
            cb_doc=self._gruel_on_doc)
    def on_instruct_gruel_condrop(self):
        self.spin_gruel_client.order_condrop()
    def on_instruct_gruel_send(self, doc):
        self.spin_gruel_client.send_document(
            doc=doc)
    #
    def _gruel_on_connect(self):
        self.nearcast.term_announce(
            s='connect')
    def _gruel_on_condrop(self, message):
        self.nearcast.term_announce(
            s='condrop [%s]'%(message))
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
            self.nearcast.client_keystroke(
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
        self.nearcast.term_plot(
            drop=0,
            rest=79,
            c=u,
            cpair=e_colpair.yellow_t)
        self.nearcast.term_plot(
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
                s='Type "quit" to quit')
            self.b_first = False
    def on_client_keystroke(self, u):
        self.line_finder.accept_string(
            s=u)
        o = ord(u)
        if o == KEY_ORD_ENTER:
            self.nearcast.term_console_newline()
        elif o == KEY_ORD_BACKSPACE:
            self.nearcast.term_console_backspace()
        else:
            self.nearcast.term_console_send_c(
                c=u)
    #
    def _console_announce(self, s):
        self.nearcast.term_announce(
            s=s)
    def _console_line(self, line):
        if line in ('q', 'quit'):
            raise SolentQuitException()
        elif line == 'start':
            self.nearcast.instruct_gruel_connect(
                server_ip=SERVER_ADDR,
                server_port=SERVER_PORT,
                password=SERVER_PASS)
        elif line == 'stop':
            self.nearcast.instruct_gruel_condrop()
        elif line == 'send':
            self.nearcast.instruct_gruel_send(
                doc=FACES_IN_THE_STREET)
        else:
            self._console_announce(
                s='syntax error')

class CogPrimer:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
    def nc_def_console(self, console):
        self.nearcast.def_console(
            console=console)

def wrap_eng(console):
    init_logging()
    engine = engine_new(
        mtu=1500)
    engine.default_timeout = 0.02
    try:
        nearcast_schema = nearcast_schema_new(
            i_nearcast=I_NEARCAST_SCHEMA)
        orb = engine.init_orb(
            orb_h=__name__,
            nearcast_schema=nearcast_schema)
        #
        orb.init_cog(CogGruelClient)
        orb.init_cog(CogShell)
        orb.init_cog(CogTerminal)
        primer = orb.init_cog(CogPrimer)
        #
        primer.nc_def_console(
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
        console = console_new(
            width=80,
            height=25)
        wrap_eng(
            console=console)
    except:
        traceback.print_exc()
    finally:
        console.close()

if __name__ == '__main__':
    main()

