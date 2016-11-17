#!/usr/bin/env python3

from solent.eng import create_engine, init_logging, log

from collections import deque
import traceback

# xxx
TERM_LINK_ADDR = '127.0.0.1'
TERM_LINK_PORT = 4100

class CogTermLink(object):
    def __init__(self, name, engine, addr, port):
        self.name = name
        self.engine = engine
        self.addr = addr
        self.port = port
        # form: (addr, port) : deque containing data
        self.received = {}
        self.server_sid = engine.open_tcp_server(
            addr=addr,
            port=port,
            cb_tcp_connect=self.engine_on_tcp_connect,
            cb_tcp_confail=self.engine_on_tcp_confail,
            cb_tcp_recv=self.engine_on_tcp_recv)
    def close(self):
        self.engine.close_tcp_server(self.server_sid)
    def engine_on_tcp_connect(self, cs_tcp_connect):
        engine = cs_tcp_connect.engine
        client_sid = cs_tcp_connect.client_sid
        addr = cs_tcp_connect.addr
        port = cs_tcp_connect.port
        #
        log("connect/%s/%s/%s/%s"%(
            self.name,
            client_sid,
            addr,
            port))
        key = (engine, client_sid)
        self.received[key] = deque()
        engine.send(
            sid=client_sid,
            data='hello, %s:%s!\n'%(addr, port))
    def engine_on_tcp_confail(self, cs_tcp_confail):
        engine = cs_tcp_confail.engine
        client_sid = cs_tcp_confail.client_sid
        message = cs_tcp_confail.message
        #
        log("confail/%s/%s/%s"%(self.name, client_sid, message))
        key = (engine, client_sid)
        del self.received[key]
    def engine_on_tcp_recv(self, cs_tcp_recv):
        engine = cs_tcp_recv.engine
        client_sid = cs_tcp_recv.client_sid
        data = cs_tcp_recv.data
        #
        key = (engine, client_sid)
        self.received[key].append(data)
        engine.send(
            sid=client_sid,
            data='received %s\n'%len(data))
    def at_turn(self):
        "Returns a boolean which is True only if there was activity."
        activity = False
        return activity

class Orb(object):
    def __init__(self, engine):
        self.engine = engine
        #
        self.cog_term_link = CogTermLink(
            name='xxx01',
            engine=self.engine,
            addr=TERM_LINK_ADDR,
            port=TERM_LINK_PORT)
    def at_turn(self):
        activity = False
        return activity

def main():
    init_logging()
    engine = create_engine()
    try:
        orb = Orb(
            engine=engine)
        engine.add_orb(orb)
        engine.event_loop()
    except KeyboardInterrupt:
        pass
    except:
        traceback.print_exc()
    finally:
        engine.close()

if __name__ == '__main__':
    main()

