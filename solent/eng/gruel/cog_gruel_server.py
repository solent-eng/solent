from solent.eng import log

from collections import deque
from collections import OrderedDict as od

class CogGruelServer(object):
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
            data='')
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
        print('recv! %s'%data) # xxx
        key = (engine, client_sid)
        self.received[key].append(data)
        engine.send(
            sid=client_sid,
            data='received %s\n'%len(data))
    def at_turn(self):
        "Returns a boolean which is True only if there was activity."
        activity = False
        return activity

def cog_gruel_server_new(name, engine, addr, port):
    ob = CogGruelServer(
        name=name,
        engine=engine,
        addr=addr,
        port=port)
    return ob



