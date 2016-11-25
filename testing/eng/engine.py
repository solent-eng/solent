from solent.util import uniq

from collections import OrderedDict as od

class Engine:
    def __init__(self):
        self.events = []
        self.sent_data = []
    def send(self, sid, data):
        self.sent_data.append(data)
    def open_tcp_client(self, addr, port, cb_tcp_connect, cb_tcp_condrop, cb_tcp_recv):
        self.events.append( ('open_tcp_client', addr, port) )

def engine_fake():
    ob = Engine()
    return ob

