from solent import Engine
from solent import log
from solent import SolentQuitException
from solent.util import SpinRoughAlarm


# --------------------------------------------------------
#   model
# --------------------------------------------------------
I_NEARCAST = '''
    i message h
    i field h

    message init
'''

class CogWaiter:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.spin_rough_alarm = engine.init_spin(SpinRoughAlarm)
    def on_init(self):
        now = self.engine.clock.now()
        self.spin_rough_alarm.book_time(
            cb_alarm_event=self.cb_alarm_event,
            value='x',
            at_t=now+2)
    def cb_alarm_event(self, cs_alarm_event):
        zero_h = cs_alarm_event.zero_h
        value = cs_alarm_event.value
        #
        log('callback! |%s|%s|'%(zero_h, value))

class CogBridge:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine

def init_nearcast(engine):
    orb = engine.init_orb(
        i_nearcast=I_NEARCAST)
    orb.init_cog(CogWaiter)
    bridge = orb.init_cog(CogBridge)
    bridge.nearcast.init()
    return bridge


# --------------------------------------------------------
#   bootstrap
# --------------------------------------------------------
MTU = 1492

def main():
    engine = Engine(
        mtu=MTU)
    try:
        init_nearcast(
            engine=engine)
        engine.event_loop()
    except KeyboardInterrupt:
        pass
    except SolentQuitException:
        pass
    finally:
        engine.close()
if __name__ == '__main__':
    main()
    
