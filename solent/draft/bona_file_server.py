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
from solent import Engine


# --------------------------------------------------------
#   model
# --------------------------------------------------------
I_NEARCAST_SCHEMA = '''
    i message h
    i field h

    message init
'''

class CogTemplate:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine

class CogBonaFileServer:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.rail_bona_file_server = RailBonaFileServer()

class CogConsole:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.
        


# --------------------------------------------------------
#   launch
# --------------------------------------------------------
MTU = 1400

def launch(engine):
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST_SCHEMA)
    orb.init_cog(CogLineConsole)
    orb.init_cog(CogInterpreter)
    orb.init_cog(CogRedisClient)
    #
    bridge = orb.init_autobridge()
    bridge.nc_init()
    #
    engine.event_loop()

def main():
    engine = Engine(
        mtu=MTU)
    try:
        launch(
            engine=engine)
    except KeyboardInterrupt:
        pass
    except SolentQuitException:
        pass
    finally:
        engine.close()

if __name__ == '__main__':
    main()


