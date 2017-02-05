#
# engine
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
# as follows:
#   - read the header for metasock.py. There's lots of edge-cases in the
#   Berkeley sockets API, and there's an unusual amount of complexity to
#   facading that. Much of what is here is explained by that priority.
#   - read from event_loop below to see what an engine instance does once
#   it has been started.
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

from .action_pool import action_pool_new
from .activity import activity_new
from .metasock import MetasockCloseCondition
from .metasock import metasock_create_sub
from .metasock import metasock_create_pub
from .metasock import metasock_create_tcp_accept
from .metasock import metasock_create_tcp_client
from .metasock import metasock_create_tcp_server
from .orb import orb_new

from solent import mempool_new
from solent import uniq
from solent.log import hexdump_bytes
from solent.log import log
from solent.util.clock import clock_new

from collections import OrderedDict as od
import select
import socket
import time
import traceback

class QuitEvent(Exception):
    def __init__(self, message=None):
        self.message = message

def eloop_debug(msg):
    log('(@) %s'%msg)

class CsMsClose:
    '''
    This exists to handle a very specific scenario. Imagine if you decide to
    close a socket during an event loop. The event loop has several stages.
    You don't want the later stages of the event loop to do things to the
    socket if it is in closing.

    This callback exists so that we can have an ignore list for things that
    are in that state.
    
    Unlike other callbacks in the file, user code should never be concerned
    with it. It is specific to the relationship between Engine and Metasock.

    You don't need to be aware of this structure you're coming to grips
    with engine/metasock. It has been deliberately kept out of cs.py to
    reduce the likelihood of end-users being confused by it.
    '''
    def __init__(self):
        self.ms = None
        self.sid = None
        self.message = None
    def __repr__(self):
        return '(%s%s)'%(self.__class__.__name__, '|'.join([str(x) for x in
            [self.ms, self.sid, self.message]]))

class Engine(object):
    def __init__(self, mtu):
        self.mtu = mtu
        #
        self.mempool = mempool_new()
        self.clock = clock_new()
        self.action_pool = action_pool_new()
        self.sid_to_metasock = od()
        self.spins = od()
        #
        self.activity = activity_new()
        self.b_debug_eloop = False
        self.sid_counter = 0
        self.default_timeout = 0.2
        self.b_nodelay = False
        #
        self.cb_ms_close = None
        self.cs_ms_close = CsMsClose()
    def enable_nodelay(self):
        self.b_nodelay = True
    def disable_nodelay(self):
        self.b_nodelay = False
    def debug_eloop_on(self):
        self.b_debug_eloop = True
    def debug_eloop_off(self):
        self.b_debug_eloop = False
    def get_clock(self):
        return self.clock
    def get_mtu(self):
        return self.mtu
    def set_default_timeout(self, value):
        self.default_timeout = value
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
                traceback.print_exc()
        for orb in self.spins.values():
            try:
                orb.at_close()
            except:
                traceback.print_exc()
    def _add_spin(self, spin_h, spin):
        at_methods = [m for m in dir(spin) if m.startswith('at_')]
        m = "Missing method. Spins need at_turn(drive) and at_close()."
        if 'at_turn' not in at_methods:
            raise Exception(m)
        if 'at_close' not in at_methods:
            raise Exception(m)
        if spin_h in self.spins:
            raise Exception("Engine already has spin_h %s"%spin_h)
        if spin in self.spins.values():
            raise Exception("Orb is already in engine. Don't double-add.")
        self.spins[spin_h] = spin
    def init_orb(self, spin_h, i_nearcast):
        '''
        Orb is a special kind of spin that does nearcasting.
        '''
        spin = orb_new(
            spin_h=spin_h,
            engine=self,
            i_nearcast=i_nearcast)
        self._add_spin(
            spin_h=spin_h,
            spin=spin)
        return spin
    def init_spin(self, construct, **kwargs):
        spin_h = '%s/%s'%(str(construct), uniq())
        spin = construct(
            spin_h=spin_h,
            engine=self,
            **kwargs)
        self._add_spin(
            spin_h=spin_h,
            spin=spin)
        return spin
    def del_spin(self, spin_h):
        # xxx unsubscribe logic if it is an orb
        del self.spins[spin_h]
    def turn(self, timeout=0):
        b_any_activity_at_all = False
        #
        # Caller's callback
        orbs_in_this_loop = list(self.spins.values())
        for orb in orbs_in_this_loop:
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
            # want no timeout in next loop
            timeout = 0
        else:
            # We are in a period of inactivity: let the next loop
            # select have some timeout.
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
    def send(self, sid, bb):
        '''This is called send to correspond to user intent.

        In fact, the bb data goes into a buffer. The event loop will get
        around to pushing that data to the network.
        
        This method makes a copy of bb. So you don't need to worry
        about the effect of subsequent writes made to that buffer.

        In short: you can call send here, know that a copy of your bb is
        in the mail, and carry on without further concern. So long as
        connectivity stays up, your user will get a copy of what was in
        bb when it was supplied to this method.
        '''
        # --------------------------------------------------------
        #   conversion logic from bb to sip
        # --------------------------------------------------------
        #
        #   !   This is only needed whilst we are switching between the
        #       new and old memory models.
        #
        sip = self.mempool.alloc(
            size=len(bb))
        sip.arr[:] = bb
        # --------------------------------------------------------
        #   standard logic
        # --------------------------------------------------------
        #log('send sid:%s data_len:%s'%(sid, len(data)))
        ms = self._get_ms_for_sid(sid)
        if not ms.can_it_send:
            raise Exception("%s does not have can_it_send"%(sid))
        if len(bb) > self.mtu:
            raise Exception('Payload size %s is larger than mtu %s'%(
                len(bb), self.mtu))
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
        #
        # Windows gives an OS error when you make a call to select with all
        # arguments being empty sets. We avoid this scenario by detecting if
        # there is no networking being done. In this case, we honour the
        # timeout with a short sleep. [Emphasis: in the current logic below,
        # xlist gets every socket in it. So if we get past this conditional,
        # there should not be further circumstances in which the Windows error
        # circumstance can be triggered.]
        if 0 == len(self.sid_to_metasock):
            time.sleep(timeout)
            return False
        #
        # Convenience for further down
        sock_to_metasock = {}
        def create_lookup_for_metasock(ms):
            sock_to_metasock[ms.sock] = ms
        #
        # Say we're doing a read, and then find that we unexpectedly need
        # to shut the socket. In this case, we want a place to buffer the
        # sockets that have been closed since the last select so we can
        # avoid processing them.
        sock_ignore_list = []
        # It is important we make a copy of this here, before the loop
        # starts running
        candidate_pairs = [pair
            for pair
            in self.sid_to_metasock.items()]
        # This function combines the items above to give you socket resources
        # that are still in play
        def active_sid_ms_pairs():
            'generator. yields (sid, ms).'
            for (sid, ms) in candidate_pairs:
                if ms.sock not in sock_ignore_list:
                    yield (sid, ms)
        #
        # All socket closes in the metasock give a callback. This allows us to
        # have cleanup functionality in a single place. The reason it's here
        # rather than in metasock is so that we can access sock_ignore_list.
        # This could probably be a global variable instead, but for the moment
        # it's no big deal.
        def cb_ms_close(cs_ms_close):
            ms = cs_ms_close.ms
            sid = cs_ms_close.sid
            message = cs_ms_close.message
            #
            sock_ignore_list.append(ms.sock)
            log('metasock %s closed [reason: %s]'%(
                cs_ms_close.ms.sid, cs_ms_close.message))
        self.cb_ms_close = cb_ms_close
        #
        # Groundwork for the select
        rlist = []
        wlist = []
        xlist = []
        for (sid, ms) in active_sid_ms_pairs():
            create_lookup_for_metasock(ms)
            if ms.desire_for_readable_select_list():
                rlist.append(ms.sock)
            if ms.desire_for_writable_select_list():
                wlist.append(ms.sock)
            xlist.append(ms.sock)
        #
        # Select
        rlist, wlist, xlist = select.select(rlist, wlist, xlist, timeout)
        #log('select /r%s /w%s /x%s /t:%s'%(rlist, wlist, xlist, timeout))
        #
        # Handle errors
        for sock in xlist:
            if sock in sock_ignore_list:
                continue
            ms = sock_to_metasock[sock]
            try:
                ms.manage_exceptionable()
            except MetasockCloseCondition as e:
                self._close_metasock(
                    sid=ms.sid,
                    reason=e.message)
        for sock in rlist:
            if sock in sock_ignore_list:
                continue
            ms = sock_to_metasock[sock]
            try:
                ms.manage_readable()
            except MetasockCloseCondition as e:
                self._close_metasock(
                    sid=ms.sid,
                    reason=e.message)
        #
        # Handle writes (and pending connections)
        for sock in wlist:
            if sock in sock_ignore_list:
                continue
            ms = sock_to_metasock[sock]
            try:
                ms.manage_writable()
            except MetasockCloseCondition as e:
                self._close_metasock(
                    sid=ms.sid,
                    reason=e.message)
        #
        # Now we are out of the loop, we can clear the callback that was
        # protecting against ships-in-the-night problems to do with sockets
        # being in a state of closing.
        self.cb_ms_close = None
        #
        # The caller may wish to use the return code to influence it on
        # the timeout that it passes in on a further iteration.
        if rlist or wlist or xlist or sock_ignore_list:
            return True
        else:
            return False
    def open_sub(self, addr, port, cb_sub_start, cb_sub_stop, cb_sub_recv):
        sid = self.create_sid()
        ms = metasock_create_sub(
            engine=self,
            mempool=self.mempool,
            sid=sid,
            addr=addr,
            port=port,
            cb_sub_start=cb_sub_start,
            cb_sub_stop=cb_sub_stop,
            cb_sub_recv=cb_sub_recv)
        return sid
    def close_sub(self, sub_sid):
        self._close_metasock(
            sid=sub_sid,
            reason='close_sub %s'%(sub_sid))
    def open_pub(self, addr, port, cb_pub_start, cb_pub_stop):
        sid = self.create_sid()
        ms = metasock_create_pub(
            engine=self,
            mempool=self.mempool,
            sid=sid,
            addr=addr,
            port=port,
            cb_pub_start=cb_pub_start,
            cb_pub_stop=cb_pub_stop)
        return sid
    def close_pub(self, pub_sid):
        self._close_metasock(
            sid=pub_sid,
            reason='close_pub %s'%(pub_sid))
    def register_tcp_accept(self, accept_sock, addr, port, parent_sid, cb_tcp_accept_connect, cb_tcp_accept_condrop, cb_tcp_accept_recv):
        """When metasock has a tcp server, it will create a new socket
        whenever it does an accept. At this point, it passes that new
        sock here so that we can set up a new metasock to manage it.
        This should never be called from outside this package."""
        accept_sid = self.create_sid()
        ms = metasock_create_tcp_accept(
            engine=self,
            mempool=self.mempool,
            sid=accept_sid,
            accept_sock=accept_sock,
            addr=addr,
            port=port,
            parent_sid=parent_sid,
            cb_tcp_accept_connect=cb_tcp_accept_connect,
            cb_tcp_accept_condrop=cb_tcp_accept_condrop,
            cb_tcp_accept_recv=cb_tcp_accept_recv)
        return accept_sid
    def close_tcp_accept(self, accept_sid):
        self._close_metasock(
            sid=accept_sid,
            reason='close_tcp_accept %s'%accept_sid)
    def open_tcp_server(self, addr, port, cb_tcp_server_start, cb_tcp_server_stop, cb_tcp_accept_connect, cb_tcp_accept_condrop, cb_tcp_accept_recv):
        sid = self.create_sid()
        ms = metasock_create_tcp_server(
            engine=self,
            mempool=self.mempool,
            sid=sid,
            addr=addr,
            port=port,
            cb_tcp_server_start=cb_tcp_server_start,
            cb_tcp_server_stop=cb_tcp_server_stop,
            cb_tcp_accept_connect=cb_tcp_accept_connect,
            cb_tcp_accept_condrop=cb_tcp_accept_condrop,
            cb_tcp_accept_recv=cb_tcp_accept_recv)
        return sid
    def close_tcp_server(self, server_sid):
        self._close_metasock(
            sid=server_sid,
            reason='close_tcp_server %s'%server_sid)
    def open_tcp_client(self, addr, port, cb_tcp_client_connect, cb_tcp_client_condrop, cb_tcp_client_recv):
        sid = self.create_sid()
        ms = metasock_create_tcp_client(
            engine=self,
            mempool=self.mempool,
            sid=sid,
            addr=addr,
            port=port,
            cb_tcp_client_connect=cb_tcp_client_connect,
            cb_tcp_client_condrop=cb_tcp_client_condrop,
            cb_tcp_client_recv=cb_tcp_client_recv)
        return sid
    def close_tcp_client(self, client_sid):
        self._close_metasock(
            sid=client_sid,
            reason='close_tcp_client %s'%client_sid)
    def _map_sid_to_metasock(self, sid, ms):
        '''
        We need to call this from the metasock factories. It must happen after
        the metasock has been created, but before the init callbacks have been
        called against the metasock. That way if any of those sockets try to
        send as part of their initialisation callbacks, the sid will be
        waiting in this map already.
        '''
        self.sid_to_metasock[sid] = ms
    def _get_ms_for_sid(self, sid):
        return self.sid_to_metasock[sid]
    def _close_metasock(self, sid, reason):
        ms = self._get_ms_for_sid(
            sid=sid)
        ms.close(reason)
        del self.sid_to_metasock[sid]
        #
        # If we are in the middle of a select loop, there is a mechanism
        # that avoids us from (example) tripping over our laces by trying to
        # read from a socket that is in shutdown. That's what this block is
        # about.
        if self.cb_ms_close != None:
            self.cs_ms_close.ms = ms
            self.cs_ms_close.message = reason
            self.cb_ms_close(
                cs_ms_close=self.cs_ms_close)

def engine_new(mtu):
    ob = Engine(
        mtu=mtu)
    return ob

