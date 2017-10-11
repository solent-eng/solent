from solent import Engine
from solent import SolentQuitException
from solent import log

import time


# --------------------------------------------------------
#   model
# --------------------------------------------------------
I_NEARCAST = '''
    i message h
    i field h

    message init
        field addr
        field port

    message ping
'''

class CogCoord:
    '''
    Every five turns, send a ping message
    '''
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.count_turns = 0
    #
    def orb_turn(self, activity):
        self.count_turns += 1
        if self.count_turns == 5:
            self.count_turns = 0
            self.nearcast.ping()

class CogUdpPublisher:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.pub_sid = None
    #
    def on_init(self, addr, port):
        self.engine.open_pub(
            addr=addr,
            port=port,
            cb_pub_start=self.cb_pub_start,
            cb_pub_stop=self.cb_pub_stop)
    def on_ping(self):
        if None == self.pub_sid:
            return
        #
        log('ping')
        msg = 'Time is now %s'%(str(time.time()))
        bb = bytes(msg, 'utf8')
        self.engine.send(
            sid=self.pub_sid,
            bb=bb)
    #
    def cb_pub_start(self, cs_pub_start):
        engine = cs_pub_start.engine
        pub_sid = cs_pub_start.pub_sid
        addr = cs_pub_start.addr
        port = cs_pub_start.port
        #
        self.pub_sid = pub_sid
        log('pub start %s'%(self.pub_sid))
    def cb_pub_stop(self, cs_pub_stop):
        engine = cs_pub_stop.engine
        pub_sid = cs_pub_stop.pub_sid
        message = cs_pub_stop.message
        #
        log('pub stop %s'%(self.pub_sid))
        self.pub_sid = None

def init(engine, addr, port):
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST)
    orb.init_cog(CogCoord)
    orb.init_cog(CogUdpPublisher)
    #
    bridge = orb.init_autobridge()
    bridge.nc_init(
        addr=addr,
        port=port)


# --------------------------------------------------------
#   launch
# --------------------------------------------------------
MTU = 1300

ADDR = '127.255.255.255'
PORT = 50000

def main():
    engine = Engine(
        mtu=MTU)
    try:
        init(
            engine=engine,
            addr=ADDR,
            port=PORT)
        engine.event_loop()
    except KeyboardInterrupt:
        pass
    except SolentQuitException:
        pass

if __name__ == '__main__':
    main()

