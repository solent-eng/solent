#
# Engine.
#
# // overview
# Network engine. This is the core class of the eng system. It provides
# something that's similar to a reactor, but it's less ambitious than other
# reactor-based systems.
#
# Maybe you're here because you're trying to understand how to use this class.
# This would be a hairy read. A better starting point would be scenarios.py.
#   * See if the thing you are trying to do is covered there. If it is, then
#     learn by example, and spare yourself the anguish of reading this system.
#   * Also, there's a FAQ at the top there.
#
# If you do decide to press on and delve into this code, I recommend you start
# by reading the header for metasock.py. There's lots of edge-cases in the
# Berkeley sockets API, and there's an unusual amount of complexity to
# facading that. Good luck.
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

from .activity import activity_new
from .metasock import MetasockCloseCondition
from .metasock import metasock_create_accepted_tcp_client
from .metasock import metasock_create_broadcast_listener
from .metasock import metasock_create_broadcast_sender
from .metasock import metasock_create_tcp_client
from .metasock import metasock_create_tcp_server
from .orb import orb_new

from solent import mempool_new
from solent.log import hexdump_bytes
from solent.log import log
from solent.util.clock import clock_new

import errno
import select
import socket
import traceback

class QuitEvent(Exception):
    def __init__(self, message=None):
        self.message = message

def eloop_debug(msg):
    log('(@) %s'%msg)

class Engine(object):
    def __init__(self, mtu):
        self.mtu = mtu
        #
        self.mempool = mempool_new()
        self.clock = clock_new()
        self.sid_to_metasock = {}
        self.orbs = {}
        #
        self.activity = activity_new()
        self.b_debug_eloop = False
        self.sid_counter = 0
        self.default_timeout = 0.2
    def debug_eloop_on(self):
        self.b_debug_eloop = True
    def debug_eloop_off(self):
        self.b_debug_eloop = False
    def get_clock(self):
        return self.clock
    def get_mtu(self):
        return self.mtu
    def set_mtu(self, mtu):
        self.mtu = mtu
    def create_sid(self):
        next = self.sid_counter
        self.sid_counter += 1
        return next
    def close(self):
        items = [pair for pair in self.sid_to_metasock.items()]
        for (sid, ms) in items:
            try:
                self._close_metasock(
                    sid=sid,
                    reason='engine_closing')
            except:
                pass
        for orb in self.orbs.values():
            orb.close()
    def add_orb(self, orb_h, orb):
        if orb_h in self.orbs:
            raise Exception("Engine already has orb_h %s"%orb_h)
        if orb in self.orbs.values():
            raise Exception("Orb is already in engine. Don't double-add.")
        self.orbs[orb_h] = orb
    def init_orb(self, orb_h, nearcast_schema):
        orb = orb_new(
            orb_h=orb_h,
            engine=self,
            nearcast_schema=nearcast_schema)
        self.add_orb(
            orb_h=orb_h,
            orb=orb)
        return orb
    def del_orb(self, orb_h):
        del self.orbs[org_h]
    def turn(self, timeout=0):
        #
        # Caller's callback
        b_any_activity_at_all = False
        for orb in self.orbs.values():
            orb.at_turn(
                activity=self.activity)
        lst_orb_activity = self.activity.get()
        if lst_orb_activity:
            self.activity.clear()
            b_any_activity_at_all = True
            if self.b_debug_eloop:
                for s in lst_orb_activity:
                    eloop_debug('*ACTIVITY* %s'%(s))
        #
        # Select
        activity_from_select = self._call_select(timeout)
        if activity_from_select:
            b_any_activity_at_all = True
            if self.b_debug_eloop:
                eloop_debug('select activity')
        #
        # If we have activity, we don't want select jamming
        # things up with delays.
        if b_any_activity_at_all:
            # i.e. nothing
            timeout = 0
        else:
            # i.e. something
            timeout = self.default_timeout
        return timeout
    def cycle(self):
        '''
        This causes a sequence of turns to run until there is no more
        activity. This can be useful for testing and troubleshooting.
        '''
        timeout = 0
        while timeout == 0:
            timeout = self.turn()
    def event_loop(self):
        '''
        Lets the engine take ownership of the application's initiative by
        running the event loop. Typically, an application would set up its
        orbs, add them to the engine, and then call this function to surrender
        initiative to the engine.
        '''
        timeout = 0
        try:
            while True:
                timeout = self.turn(
                    timeout=timeout)
        except QuitEvent as e:
            log('QuitEvent [%s]'%(e.message))
    def send(self, sid, payload):
        '''This is called send to correspond to user intent.

        In fact, the payload data goes into a buffer. The event loop will get
        around to pushing that data to the network.
        
        This method makes a copy of payload. So you don't need to worry
        about the effect of subsequent writes made to that buffer.

        In short: you can call send here, know that a copy of your payload is
        in the mail, and carry on without further concern. So long as
        connectivity stays up, your user will get a copy of what was in
        payload when it was supplied to this method.
        '''
        # --------------------------------------------------------
        #   conversion logic from payload to sip
        # --------------------------------------------------------
        #
        #   !   This is only needed whilst we are switching between the
        #       new and old memory models.
        #
        sip = self.mempool.alloc(
            size=len(payload))
        sip.arr[:] = payload
        # --------------------------------------------------------
        #   standard logic
        # --------------------------------------------------------
        #log('send sid:%s data_len:%s'%(sid, len(data)))
        ms = self._get_ms_for_sid(sid)
        if not ms.can_it_send:
            raise Exception("%s does not have can_it_send"%(sid))
        if len(payload) > self.mtu:
            raise Exception('Payload size %s is larger than mtu %s'%(
                len(payload), self.mtu))
        ms.copy_to_send_queue(
            sip=sip)
        # --------------------------------------------------------
        #   cleanup of converstion logic
        # --------------------------------------------------------
        #
        # This will need to go also
        #
        self.mempool.free(
            sip=sip)
    def _call_select(self, timeout=0):
        "Return True or False depending on whether or not there was activity."
        sock_to_metasock = {}
        def create_lookup_for_metasock(ms):
            sock_to_metasock[ms.sock] = ms
        #
        # Say we're doing a read, and then find that we unexpectedly need
        # to shut the socket. In this case, we want a place to buffer the
        # sockets that have been closed since the last select so we can
        # avoid processing them.
        sock_ignore_list = []
        #
        # All socket closes in the metasock give a callback. This allows us to
        # have cleanup functionality in a single place. The reason it's here
        # rather than in metasock is so that we can access sock_ignore_list.
        # This could probably be a global variable instead, but for the moment
        # it's no big deal.
        def cb_ms_close(cs_ms_close):
            sock_ignore_list.append(cs_ms_close.ms.sock)
            log('metasock %s closed [reason: %s]'%(
                cs_ms_close.ms.sid, cs_ms_close.message))
        #
        # It seems inefficient and laborious to set this on every pass, but
        # at the moment it's not a big deal.
        items_for_this_eloop = [pair for pair in self.sid_to_metasock.items()]
        for (sid, ms) in items_for_this_eloop:
            ms.cb_ms_close = cb_ms_close
        #
        # Handle TCP clients who are in the process of connecting. The call
        # below on a successful connection is weird. I can't find a cleaner
        # way to encapsulate the logic. I think this could be useful if ever
        # I'm looking for an example that highlights the odd design of the
        # bsd sockets api.
        for (sid, ms) in items_for_this_eloop:
            if ms.is_tcp_client_connecting:
                ec = ms.sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                if 0 == ec:
                    ms.successful_connection_as_tcp_client()
                elif 'EINPROGRESS' == errno.errorcode[ec]:
                    sock_ignore_list.append(ms.sock)
                else:
                    sock_ignore_list.append(ms.sock)
                    r = ' '.join( [ 'Unable to connect to'
                                  , '%s:%s'%(ms.addr, ms.port)
                                  , '[%s:%s]'%(ec, errno.errorcode[ec])
                                  ] )
                    self._close_metasock(
                        sid=sid,
                        reason=r)
        #
        # Groundwork for the select
        rlst = []
        wlst = []
        elst = []
        for (sid, ms) in items_for_this_eloop:
            if ms.sock in sock_ignore_list:
                continue
            create_lookup_for_metasock(ms)
            if ms.desires_recv():
                rlst.append(ms.sock)
            if ms.desires_send():
                wlst.append(ms.sock)
            elst.append(ms.sock)
        #
        # Select
        rlst, wlst, elst = select.select(rlst, wlst, elst, timeout)
        #log('select %s|%s|%s|%s'%(timeout, rlst, wlst, elst))
        #
        # Handle errors
        for sock in elst:
            if sock in sock_ignore_list:
                continue
            ms = sock_to_metasock[sock]
            self._close_metasock(
                sid=ms.sid,
                reason='select_elst')
        #
        # Handle reads
        for sock in rlst:
            if sock in sock_ignore_list:
                continue
            ms = sock_to_metasock[sock]
            try:
                ms.manage_recv(
                    cb_ms_close=cb_ms_close)
            except MetasockCloseCondition as e:
                self._close_metasock(
                    sid=ms.sid,
                    reason=e.message)
        #
        # Handle writes
        for sock in wlst:
            if sock in sock_ignore_list:
                continue
            ms = sock_to_metasock[sock]
            try:
                ms.manage_send()
            except MetasockCloseCondition as e:
                self._close_metasock( sid=ms.sid
                                    , reason=e.message
                                    )
        #
        # The caller may wish to use the return code to influence it on
        # the timeout that it passes in on a further iteration.
        if rlst or wlst or elst or sock_ignore_list:
            return True
        else:
            return False
    def register_accepted_tcp_csock(self, csock, addr, port, cb_tcp_condrop, cb_tcp_recv, cb_ms_close):
        """When metasock has a tcp server, it will create a new socket
        whenever it does an accept. At this point, it passes that new
        sock here so that we can set up a new metasock to manage it."""
        client_sid = self.create_sid()
        ms = metasock_create_accepted_tcp_client(
            engine=self,
            mempool=self.mempool,
            sid=client_sid,
            csock=csock,
            addr=addr,
            port=port,
            cb_tcp_condrop=cb_tcp_condrop,
            cb_tcp_recv=cb_tcp_recv,
            cb_ms_close=cb_ms_close)
        self.sid_to_metasock[client_sid] = ms
        return client_sid
    def open_broadcast_listener(self, addr, port, cb_sub_recv):
        sid = self.create_sid()
        ms = metasock_create_broadcast_listener(
            engine=self,
            mempool=self.mempool,
            sid=sid,
            addr=addr,
            port=port,
            cb_sub_recv=cb_sub_recv)
        self.sid_to_metasock[sid] = ms
        return sid
    def close_broadcast_listener(self, sid):
        self._close_metasock(sid, 'close_broadcast_listener %s'%(sid))
    def open_broadcast_sender(self, addr, port):
        sid = self.create_sid()
        ms = metasock_create_broadcast_sender(
            engine=self,
            mempool=self.mempool,
            sid=sid,
            addr=addr,
            port=port)
        self.sid_to_metasock[sid] = ms
        return sid
    def close_broadcast_sender(self, sid):
        self._close_metasock(sid, 'close_broadcast_sender %s'%(sid))
    def open_tcp_server(self, addr, port, cb_tcp_connect, cb_tcp_condrop, cb_tcp_recv):
        sid = self.create_sid()
        ms = metasock_create_tcp_server(
            engine=self,
            mempool=self.mempool,
            sid=sid,
            addr=addr,
            port=port,
            cb_tcp_connect=cb_tcp_connect,
            cb_tcp_condrop=cb_tcp_condrop,
            cb_tcp_recv=cb_tcp_recv)
        self.sid_to_metasock[sid] = ms
        return sid
    def close_tcp_server(self, sid):
        self._close_metasock(sid, 'close_tcp_server')
    def open_tcp_client(self, addr, port, cb_tcp_connect, cb_tcp_condrop, cb_tcp_recv):
        sid = self.create_sid()
        ms = metasock_create_tcp_client(
            engine=self,
            mempool=self.mempool,
            sid=sid,
            addr=addr,
            port=port,
            cb_tcp_connect=cb_tcp_connect,
            cb_tcp_condrop=cb_tcp_condrop,
            cb_tcp_recv=cb_tcp_recv)
        self.sid_to_metasock[sid] = ms
        return sid
    def close_tcp_client(self, sid):
        self._close_metasock(sid, 'close_tcp_client')
    def _get_ms_for_sid(self, sid):
        return self.sid_to_metasock[sid]
    def _close_metasock(self, sid, reason):
        ms = self._get_ms_for_sid(sid)
        ms.close(reason)
        del self.sid_to_metasock[sid]

def engine_new(mtu):
    ob = Engine(
        mtu=mtu)
    return ob

