#!/usr/bin/env python3
#
# Gruel server sandbox
#
# // brief
# Demonstrates an application that incorporated a gruel server.
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

from solent.eng import engine_new
from solent.eng import nearcast_schema_new
from solent.gruel import spin_gruel_server_new
from solent.lc import spin_line_console_new
from solent.log import cformat
from solent.log import init_logging
from solent.log import log

from collections import deque
import traceback

SERVER_ADDR = '127.0.0.1'
SERVER_PORT = 4100
SERVER_PASS = 'qweasd'

SNOOP_ADDR = '127.0.0.1'
SNOOP_PORT = 4090

LC_ADDR = '127.0.0.1'
LC_PORT = 4091

I_NEARCAST_SCHEMA = '''
    i message h
    i field h

    message lc_input
        field line
    
    message lc_output
        field s

    message start_gruel_server
        field addr
        field port
        field password

    message permit_client_ip
        field ip

    message stop_gruel_server

    message doc_recv
        field doc

    message doc_send
        field doc
'''

MAN_FROM_SNOWY_RIVER = '''
--------------------------------------------------------
The Man From Snowy River

There was movement at the station, for the word had passed around
That the colt from Old Regret had got away,
And had joined the wild bush horses--he was worth a thousand pound,
So all the cracks had gathered to the fray
All the tried and noted riders from the stations near and far
Had mustered at the homestead overnight,
For the bushmen love hard riding where the wild bush horses are,
And the stock-horse snuffs the battle with delight,

There was Harrison, who made his pile when Pardon won the cup,
The old man with his hair as white as snow;
But few could ride beside him when his blood was fairly up--
He would go wherever horse and man could go.
And Clancy of the Overflow came down to lend a hand,
No better horseman ever held the reins;
For never horse could throw him while the saddle-girths would stand--
He learnt to ride while droving on the plains.

And one was there, a stripling on a small and weedy beast;
He was something like a racehorse undersized,
With a touch of Timor pony--three parts thoroughbred at least--
And such as are by mountain horsemen prized.
He was hard and tough and wiry--just the sort that won't say die--
There was courage in his quick impatient tread;
And he bore the badge of gameness in his bright and fiery eye
And the proud and lofty carriage of his head.

But still so slight and weedy, one would doubt his power to stay,
And the old man said, "That horse will never do
For a long and tiring gallop--lad, you'd better stop away,
Those hills are far too rough for such as you."
So he waited, sad and wistful--only Clancy stood his friend--
"I think we ought to let him come," he said;
"I warrant he'll be with us when he's wanted at the end,
For both his horse and he are mountain bred.

"He hails from Snowy River, up by Kosciusko's side,
Where the hills are twice as steep and twice as rough;
Where the horse's hoofs strike firelight from the flint stones every stride,
The man that holds his own is good enough
And the Snowy River riders on the mountains make their home,
Where the river runs those giant hills between;
I have seen full many horsemen since I first commenced to roam
But nowhere yet such horsemen have I seen."

So he went; they found the horses by the big mimosa clump,
They raced away towards the mountain's brow,
And the old man gave his orders, "Boys, go at them from the jump,
No use to try the fancy riding now
And Clancy, you must wheel them, try and wheel them to the right,
Ride boldly, lad, and never fear the spills,
For never yet was rider that could keep the mob in sight,
If once they gain the shelter of those hills."

So Clancy rode to wheel them--he was racing on the wing
Where the best and boldest riders take their place,
And he raced his stock-horse past them, and he made the ranges ring
With the stockwhip, as he met them face to face.
Then they halted for a moment, while he swung the dreaded lash,
And they saw their well-loved mountain full in view,
And they charged beneath the stockwhip with a sharp and sudden dash,
And off into the mountain scrub they flew.

Then fast the horsemen followed, where the gorges deep and black
Resounded to the thunder of their tread,
And the stockwhips woke the echoes, and they fiercely answered back
From cliffs and crags that beetled overhead.
And upward, ever upward, the wild horses held their way,
Where mountain ash and kurrajong grew wide;
And the old man muttered fiercely, "We may bid the mob good day,
No man can hold them down the other side."

When they reached the mountain's summit, even Clancy took a pull--
It well might make the boldest hold their breath;
The wild hop scrub grew thickly, and the hidden ground was full
Of wombat holes, and any slip was death,
But the man from Snowy River let the pony have his head,
And he swung his stockwhip round and gave a cheer,
And he raced him down the mountain like a torrent down its bed,
While the others stood and watched in very fear.

He sent the flint-stones flying, but the pony kept his feet,
He cleared the fallen timber in his stride,
And the man from Snowy River never shifted in his seat--
It was grand to see that mountain horseman ride.
Through the stringy barks and saplings, on the rough and broken ground,
Down the hillside at a racing pace he went;
And he never drew the bridle till he landed safe and sound
At the bottom of that terrible descent.

He was right among the horses as they climbed the farther hill,
And the watchers on the mountain, standing mute,
Saw him ply the stockwhip fiercely; he was right among them still,
As he raced across the clearing in pursuit.
Then they lost him for a moment, where two mountain gullies met
In the ranges--but a final glimpse reveals
On a dim and distant hillside the wild horses racing yet,
With the man from Snowy River at their heels.

And he ran them single-handed till their sides were white with foam;
He followed like a bloodhound on their track,
Till they halted, cowed and beaten; then he turned their heels for home,
And alone and unassisted brought them back.
But his hardy mountain pony he could scarcely raise a trot,
He was blood from hip to shoulder from the spur;
But his pluck was still undaunted, and his courage fiery hot,
For never yet was mountain horse a cur.

And down by Kosciusko, where the pine-clad ridges raise
Their torn and rugged battlements on high,
Where the air is clear as crystal, and the white stars fairly blaze
At midnight in the cold and frosty sky,
And where around the Overflow the reed-beds sweep and sway
To the breezes, and the rolling plains are wide,
The Man from Snowy River is a household word to-day,
And the stockmen tell the story of his ride.
++++++++++++++++++++++++++++++++++++++++++++++++++++++++
'''

class CogLcServer:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.spin_line_console = spin_line_console_new(
            engine=engine,
            cb_line=self.lc_on_line)
        self.spin_line_console.start(
            ip=LC_ADDR,
            port=LC_PORT)
    #
    def lc_on_line(self, line):
        self.nearcast.lc_input(
            line=line)
    #
    def on_lc_output(self, s):
        col = cformat(
            string=s,
            fg='yellow',
            bg='trans')
        self.spin_line_console.write_to_client(
            s='%s\n'%(col))

class CogInterpretLineConsole:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.commands = {
            'start': self.cmd_start,
            'send': self.cmd_send,
            'stop': self.cmd_stop,
            '?': self.cmd_help,
            'help': self.cmd_help}
    #
    def on_lc_input(self, line):
        # This is really primitive not even going to parse it. :)
        line = line.strip()
        if line not in self.commands:
            self.nearcast.lc_output(
                s='syntax error')
            return
        cmd = self.commands[line]
        cmd()
    #
    def cmd_start(self):
        self.nearcast.start_gruel_server(
            addr=SERVER_ADDR,
            port=SERVER_PORT,
            password=SERVER_PASS)
    def cmd_send(self):
        self.nearcast.doc_send(
            doc=MAN_FROM_SNOWY_RIVER)
    def cmd_stop(self):
        self.nearcast.stop_gruel_server()
    def cmd_help(self):
        self.nearcast.lc_output(
            s='\n'.join(sorted(self.commands.keys())))

class CogGruelServer:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.spin_gruel_server = spin_gruel_server_new(
            engine=engine,
            cb_doc_recv=self._gruel_on_doc)
        #
        self.at_start()
    def at_start(self):
        self.spin_gruel_server.start(
            addr=SERVER_ADDR,
            port=SERVER_PORT,
            password=SERVER_PASS)
    def at_turn(self, activity):
        self.spin_gruel_server.at_turn(
            activity=activity)
    def on_start_gruel_server(self, addr, port, password):
        self.spin_gruel_server.start(
            addr=addr,
            port=port,
            password=password)
    def on_permit_client_ip(self, ip):
        self.spin_gruel_server.enable_ip(
            ip=ip)
    def on_doc_send(self, doc):
        self.spin_gruel_server.send_doc(
            doc=doc)
    def _gruel_on_doc(self, doc):
        self.nearcast.doc_recv(
            doc=doc)

class CogDocReceiver:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
    def on_doc_recv(self, doc):
        log('doc received {%s}'%(doc))

class CogUplink:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
    def nc_permit_client_ip(self, ip):
        self.nearcast.permit_client_ip(
            ip=ip)

def main():
    init_logging()
    engine = engine_new(
        mtu=1500)
    try:
        nearcast_schema = nearcast_schema_new(
            i_nearcast=I_NEARCAST_SCHEMA)
        orb = engine.init_orb(
            orb_h=__name__,
            nearcast_schema=nearcast_schema)
        orb.add_log_snoop()
        #
        orb.init_cog(CogLcServer)
        orb.init_cog(CogInterpretLineConsole)
        orb.init_cog(CogGruelServer)
        orb.init_cog(CogDocReceiver)
        #
        uplink = orb.init_cog(CogUplink)
        uplink.nc_permit_client_ip(
            ip='127.0.0.1')
        #
        engine.event_loop()
    except KeyboardInterrupt:
        pass
    except:
        traceback.print_exc()
    finally:
        engine.close()

if __name__ == '__main__':
    main()

