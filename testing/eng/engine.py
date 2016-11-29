from solent.util import uniq

from testing.util import clock_fake

class Engine:
    def __init__(self):
        #
        self.clock = clock_fake()
        self.events = []
        self.sent_data = []
    def get_clock(self):
        return self.clock
    def send(self, sid, data):
        self.sent_data.append(data[:])
    def open_tcp_client(self, addr, port, cb_tcp_connect, cb_tcp_condrop, cb_tcp_recv):
        self.events.append( ('open_tcp_client', addr, port) )
        return 'fake_sid_%s'%uniq()
    def open_tcp_server(self, addr, port, cb_tcp_connect, cb_tcp_condrop, cb_tcp_recv):
        self.events.append( ('open_tcp_server', addr, port) )
        return 'fake_sid_%s'%uniq()
    def close_tcp_server(self, sid):
        self.events.append( ('close_tcp_server',) )
    def close_tcp_client(self, sid):
        self.events.append( ('close_tcp_client',) )

def engine_fake():
    ob = Engine()
    return ob

