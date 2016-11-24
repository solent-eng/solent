from solent.util import uniq

from collections import OrderedDict as od

class Engine:
    def __init__(self):
        self.events = []
    def open_tcp_client(self, addr, port, cb_tcp_connect, cb_tcp_condrop, cb_tcp_recv):
        self.events.append( ('open_tcp_client', addr, port) )

def engine_fake():
    ob = Engine()
    return ob

