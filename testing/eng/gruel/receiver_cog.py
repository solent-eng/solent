#
# receiver cog
#
# with a bit of work work it should be possible to generate these from the
# schema.
#

from solent.log import log

class ReceiverCog:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.acc_nearnote = []
        self.acc_ipval_add_ip = []
        self.acc_ipval_disable = []
        self.acc_start_service = []
        self.acc_stop_service = []
        self.acc_announce_tcp_connect = []
        self.acc_announce_tcp_condrop = []
        self.acc_please_tcp_boot = []
        self.acc_gruel_recv = []
        self.acc_gruel_send = []
        self.acc_announce_login = []
        self.acc_doc_recv = []
        self.acc_doc_send = []
        self.acc_heartbeat_recv = []
        self.acc_heartbeat_send = []
    #
    def on_nearnote(self, s):
        self.acc_nearnote.append(s)
    def count_nearnote(self):
        return len(self.acc_nearnote)
    def get_nearnote(self):
        return self.acc_nearnote
    def last_nearnote(self):
        return self.acc_nearnote[-1]
    def log_nearnote(self):
        for l in self.acc_nearnote:
            log(l)
    #
    def nc_ipval_add_ip(self, ip):
        self.orb.nearcast(
            cog_h=self.cog_h,
            message_h='ipval_add_ip',
            ip=ip)
        self.orb.cycle()
    def on_ipval_add_ip(self, ip):
        self.acc_ipval_add_ip.append( (ip,) )
    #
    def nc_ipval_disable(self):
        self.orb.nearcast(
            cog_h=self.cog_h,
            message_h='ipval_disable')
        self.orb.cycle()
    def on_ipval_disable(self):
        self.acc_ipval_disable.append( None )
    #
    def nc_start_service(self, ip, port, password):
        self.orb.nearcast(
            cog_h=self.cog_h,
            message_h='start_service',
            ip=ip,
            port=port,
            password=password)
        self.orb.cycle()
    def on_start_service(self, ip, port, password):
        self.acc_start_service.append( (ip, port, password) )
    #
    def nc_stop_service(self):
        self.orb.nearcast(
            cog_h=self.cog_h,
            message_h='stop_service')
        self.orb.cycle()
    def on_stop_service(self):
        self.acc_stop_service.append( None )
    #
    def count_announce_tcp_connect(self):
        return len(self.acc_announce_tcp_connect)
    def last_announce_tcp_connect(self):
        return self.acc_announce_tcp_connect[-1]
    def log_announce_tcp_connect(self):
        for l in self.acc_announce_tcp_connect:
            log(l)
    def nc_announce_tcp_connect(self, ip, port):
        self.orb.nearcast(
            cog_h=self.cog_h,
            message_h='announce_tcp_connect',
            ip=ip,
            port=port)
        self.orb.cycle()
    def on_announce_tcp_connect(self, ip, port):
        self.acc_announce_tcp_connect.append( (ip, port) )
    #
    def count_announce_tcp_condrop(self):
        return len(self.acc_announce_tcp_condrop)
    def last_announce_tcp_condrop(self):
        return self.acc_announce_tcp_condrop[-1]
    def log_announce_tcp_condrop(self):
        for l in self.acc_announce_tcp_condrop:
            log(l)
    def nc_announce_tcp_condrop(self):
        self.orb.nearcast(
            cog_h=self.cog_h,
            message_h='announce_tcp_condrop')
        self.orb.cycle()
    def on_announce_tcp_condrop(self):
        self.acc_announce_tcp_condrop.append( None )
    #
    def nc_please_tcp_boot(self):
        self.orb.nearcast(
            cog_h=self.cog_h,
            message_h='please_tcp_boot')
        self.orb.cycle()
    def on_please_tcp_boot(self):
        self.acc_please_tcp_boot.append( None )
    def count_please_tcp_boot(self):
        return len(self.acc_please_tcp_boot)
    #
    def count_gruel_recv(self):
        return len(self.acc_gruel_recv)
    def last_gruel_recv(self):
        return self.acc_gruel_recv[-1]
    def on_gruel_recv(self, d_gruel):
        self.acc_gruel_recv.append(d_gruel)
    def nc_gruel_recv(self, d_gruel):
        self.orb.nearcast(
            cog_h=self.cog_h,
            message_h='gruel_recv',
            d_gruel=d_gruel)
    #
    def count_gruel_send(self):
        return len(self.acc_gruel_send)
    def last_gruel_send(self):
        return self.acc_gruel_send[-1]
    def on_gruel_send(self, d_gruel):
        log('on_gruel_send') # xxx
        self.acc_gruel_send.append(d_gruel)
    def nc_gruel_send(self, d_gruel):
        self.orb.nearcast(
            cog_h=self.cog_h,
            message_h='gruel_send',
            d_gruel=d_gruel)
    #
    def count_announce_login(self):
        return len(self.acc_announce_login)
    def last_announce_login(self):
        return self.acc_announce_login[-1]
    def nc_announce_login(self, max_packet_size, max_doc_size):
        self.orb.nearcast(
            cog_h=self.cog_h,
            message_h='announce_login',
            max_packet_size=max_packet_size,
            max_doc_size=max_doc_size)
    def on_announce_login(self, max_packet_size, max_doc_size):
        self.acc_announce_login.append( (max_packet_size, max_doc_size) )
    #
    def on_doc_recv(self, doc):
        self.acc_doc_recv.append(doc)
    def count_doc_recv(self):
        return len(self.acc_doc_recv)
    def last_doc_recv(self):
        return self.acc_doc_recv[-1]
    #
    def on_doc_send(self, doc):
        self.acc_doc_send.append(doc)
    def count_doc_send(self):
        return len(self.acc_doc_send)
    def last_doc_send(self):
        return self.acc_doc_send[-1]
    #
    def on_heartbeat_recv(self):
        self.acc_heartbeat_recv.append(None)
    def count_heartbeat_recv(self):
        return len(self.acc_heartbeat_recv)
    def last_heartbeat_recv(self):
        return self.acc_heartbeat_recv[-1]
    #
    def on_heartbeat_send(self):
        self.acc_heartbeat_send.append(None)
    def count_heartbeat_send(self):
        return len(self.acc_heartbeat_send)
    def last_heartbeat_send(self):
        return self.acc_heartbeat_send[-1]

def receiver_cog_fake(cog_h, orb, engine):
    ob = ReceiverCog(
        cog_h=cog_h,
        orb=orb,
        engine=engine)
    return ob

