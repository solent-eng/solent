#!/usr/bin/env python3
#
# Sandbox
#
# // brief
# This is being used for developing new functionality.
#
# // deprecated
# This will disappear in time. Don't use it as a dependency.
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

from solent.eng import create_engine
from solent.eng import cog_gruel_server_new
from solent.eng import nearcast_orb_new
from solent.eng import nearcast_schema_new
from solent.eng import nearcast_snoop_new
from solent.log import init_logging
from solent.log import log

from collections import deque
import traceback

# xxx
TERM_LINK_ADDR = '127.0.0.1'
TERM_LINK_PORT = 4100

I_NEARCAST_SCHEMA = '''
    i message h
    i field h
    
    message send_something
        field text
'''

def create_orb(engine):
    orb = nearcast_orb_new(
        engine=engine,
        nearcast_schema=nearcast_schema_new(
            i_nearcast=I_NEARCAST_SCHEMA))
    orb.add_cog(
        cog=cog_gruel_server_new(
            name='server01',
            engine=engine,
            addr=TERM_LINK_ADDR,
            port=TERM_LINK_PORT))
    return orb

def main():
    init_logging()
    engine = create_engine()
    try:
        engine.add_orb(
            orb=create_orb(
                engine=engine))
        engine.event_loop()
    except KeyboardInterrupt:
        pass
    except:
        traceback.print_exc()
    finally:
        engine.close()

if __name__ == '__main__':
    main()

