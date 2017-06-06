#
# orb
#
# // overview
# The orb is special type of spin. It contains an in-process broadcast
# network of actors, each of which is called a cog. Cogs can communicate
# with one another by sending broadcasts.
#
# The orb is the main workhorse for the engine. It combines a nearcast
# (see below) and easily contains cogs.
#
# An orb satisfies these needs:
# 1) It provides a nearcast. That is, a mechanism by which cogs can talk to
# one another without requiring knowlede of each other's internal state.
# 2) It bridges power from the engine to groups of cogs. On each pass of its
# event loop, an engine will run through its list of registered orbs and call
# orb.eng_turn. The orb will then call the eng_turn method for any cog that
# offers it.
#
# If you've made it this far, you might appreciate this feature of an orb:
# It's possible for multiple logical applications to run in a single process
# and under a single engine. Once we have this model in place, it becomes
# trivial to scale applications by moving them off nearcasts (in-process on
# a single piece of hardware) and onto broadcasts (multiple pieces of
# hardware) with no changes to business logic.
#
# There's a bit going on here. It could be more explained with a short video
# and some lego. To be done.
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
#

from .activity import activity_new
from .nearcast_schema import nearcast_schema_new

from solent import uniq
from solent import SolentQuitException
from solent.log import log

from collections import deque
from collections import OrderedDict as od
import inspect
from pprint import pprint
import types

class FileSnoop:
    def __init__(self, orb, nearcast_schema, filename):
        self.orb = orb
        self.nearcast_schema = nearcast_schema
        self.filename = filename
        #
        self.f_ptr = open(filename, 'w+')
        log('Logging to %s'%filename)
    def orb_close(self):
        self.f_ptr.close()
    #
    def on_nearcast_message(self, cog_h, message_h, d_fields):
        def format_message():
            sb = []
            sb.append('%s/%s '%(cog_h, message_h))
            for idx, key in enumerate(self.nearcast_schema[message_h]):
                if idx > 0:
                    sb.append(', ')
                sb.append('%s:%s'%(key, d_fields[key]))
            sb.append('\n')
            return ''.join(sb)
        nice = format_message()
        self.f_ptr.write(nice)
        self.f_ptr.flush()

class LogSnoop:
    '''
    Logs any message seen on the associated nearcast.
    '''
    def __init__(self, orb, nearcast_schema):
        self.orb = orb
        self.nearcast_schema = nearcast_schema
    def orb_close(self):
        pass
    #
    def on_nearcast_message(self, cog_h, message_h, d_fields):
        def format_message():
            sb = []
            sb.append('[%s/%s/%s] '%(self.orb.spin_h, cog_h, message_h))
            for idx, key in enumerate(self.nearcast_schema[message_h]):
                if idx > 0:
                    sb.append(', ')
                sb.append('%s:%s'%(key, d_fields[key]))
            return ''.join(sb)
        nice = format_message()
        log(nice)

class BridgeFoundation:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine

T_BRIDGE_NEARCAST_METHOD = '''
def nc_%s(self, %s):
    self.nearcast.%s(%s)
'''

def attach_bridge_nc_method_to_cog(cog, mname, fnames):
    nc_name = 'nc_%s'%mname
    cs_fields = ', '.join(fnames)
    #
    lines = []
    for (idx, fname) in enumerate(fnames):
        if idx == 0:
            lines.append('')
        lines.append('        %s=%s,'%(fname, fname))
    if lines:
        # get rid of trailing comma on last line
        last = lines.pop()
        last = last[:-1]
        lines.append(last)
    #
    code = T_BRIDGE_NEARCAST_METHOD%(
        mname, cs_fields, mname, '\n'.join(lines))
    exec(code)
    fn = locals()[nc_name]
    method = types.MethodType(fn, cog)
    setattr(cog, nc_name, method)

ORB_METADATA_H = '_orb_metadata_ns'

class OrbMetadata:
    def __init__(self):
        self.has_orb_turn = False
        self.has_orb_close = False
        self.consumes = []

def install_orb_metadata(ob):
    orb_md = OrbMetadata()
    #
    d = dir(ob)
    if 'orb_turn' in d:
        orb_md.has_orb_turn = True
    if 'orb_close' in d:
        orb_md.has_orb_close = True
    for mname in d:
        if not mname.startswith('on_'):
            continue
        vname = '_'.join(mname.split('_')[1:])
        orb_md.consumes.append(vname)
    #
    setattr(ob, ORB_METADATA_H, orb_md)

class Orb:
    def __init__(self, spin_h, engine, i_nearcast):
        self.spin_h = spin_h
        self.engine = engine
        self.i_nearcast = i_nearcast
        #
        self.nearcast_schema = nearcast_schema_new(
            i_nearcast=i_nearcast)
        #
        self.snoops = []
        self.tracks = []
        self.cogs = []
        self.pending = deque()
    def eng_turn(self, activity):
        #
        self.distribute()
        #
        for cog in self.cogs:
            orb_md = getattr(cog, ORB_METADATA_H)
            if orb_md.has_orb_turn:
                cog.orb_turn(
                    activity=activity)
    def eng_close(self):
        for snoop in self.snoops:
            snoop.orb_close()
        for cog in self.cogs:
            orb_md = getattr(cog, ORB_METADATA_H)
            if orb_md.has_orb_close:
                cog.orb_close()
    #
    def set_spin_h(self, spin_h):
        self.spin_h = spin_h
    def add_file_snoop(self, filename):
        snoop = FileSnoop(
            orb=self,
            nearcast_schema=self.nearcast_schema,
            filename=filename)
        self.snoops.append(snoop)
    def add_log_snoop(self):
        snoop = LogSnoop(
            orb=self,
            nearcast_schema=self.nearcast_schema)
        self.snoops.append(snoop)
    def init_cog(self, construct):
        cog = construct(
            cog_h=construct.__name__,
            orb=self,
            engine=self.engine)
        self._add_cog(
            cog=cog)
        return cog
    def init_autobridge(self):
        '''
        Creates a cog that has nc_ methods for each of the messages in the
        nearcast.
        '''
        cog = self.init_cog(
            construct=BridgeFoundation)
        for (message_h, fields) in self.nearcast_schema.messages.items():
            attach_bridge_nc_method_to_cog(
                cog=cog,
                mname=message_h,
                fnames=fields)
        return cog
    def init_track(self, construct):
        '''
        construct must have no arguments, and will typically be the __init__
        method of a track class. (Limiting arguments to the orb is deliberate.
        It discourages abuse. Their purpose is to listen for things, not to
        act on information. Acting is done by cogs.)
        '''
        track = construct(
            orb=self)
        #
        # validate that the track's on_methods match the schema
        on_methods = [m for m in dir(track) if m.startswith('on_')]
        for om_name in on_methods:
            method = getattr(track, om_name)
            args = inspect.getargspec(method).args
            if args[0] != 'self':
                raise Exception("track method %s should have arg 'self'."%(
                    om_name))
            args = args[1:]
            message_h = om_name[3:]
            if not self.nearcast_schema.has_message(message_h):
                m = "Cog has %s but there is no message %s in schema."%(
                    om_name, message_h)
                raise Exception(m)
            desired_args = self.nearcast_schema.get_args_for_message(
                message_h=message_h)
            if desired_args != args:
                sb = [ "Nearcast schema message [%s]"%(message_h)
                     , "defines these args: [%s]"%('|'.join(desired_args))
                     , "but %s.%s"%(track.__class__.__name__, om_name)
                     , "params are inconsistent: [%s]"%('|'.join(args))
                     ]
                raise Exception(' '.join(sb))
        #
        # validate the dev has not attempted to create turn or close methods.
        if 'orb_turn' in dir(track):
            raise Exception("Tracks are not allowed to orb_turn. (%s)"%(
                str(track)))
        if 'orb_close' in dir(track):
            raise Exception("Tracks are not allowed to orb_close. (%s)"%(
                str(track)))
        #
        install_orb_metadata(track)
        #
        self.tracks.append(track)
        return track
    def init_test_bridge_cog(self):
        cog = self.nearcast_schema.init_test_bridge_cog(
            cog_h='test_receiver/%s'%(uniq()),
            orb=self,
            engine=self.engine)
        return cog
    def nearcast(self, cog, message_h, **d_fields):
        '''
        You probably don't need to call this directly. When cogs are
        initiatlised, they have a nearcast sender injected into them.
        Use that. (self.nearcast.MESSAGE_NAME(args))
        '''
        if 'cog_h' not in dir(cog):
            raise Exception("Looks like an invalid cog arg. Has no cog_h. %s"%(
                str(cog)))
        elif None == cog:
            cog_h = 'None'
        else:
            cog_h = cog.cog_h
        if message_h not in self.nearcast_schema:
            raise Exception("Unknown message type, [%s]"%(message_h))
        mfields = self.nearcast_schema[message_h]
        if sorted(d_fields.keys()) != sorted(mfields):
            raise Exception('inconsistent fields. need %s. got %s'%(
                str(mfields), str(d_fields.keys())))
        #
        # It is important that we buffer all the messages to be sequenced, and
        # then actually send them out later on in distribute. Otherwise we can
        # end up in a situation where actors have hijacked activity away from
        # the event loop, and a starvation scenario.
        self.pending.append( (cog_h, message_h, d_fields) )
    def distribute(self):
        '''
        The engine event loop will call this. Messages which have been
        buffered to be nearcast are sent out to the cogs.
        '''
        while self.pending:
            (cog_h, message_h, d_fields) = self.pending.popleft()
            rname = 'on_%s'%message_h
            for snoop in self.snoops:
                snoop.on_nearcast_message(
                    cog_h=cog_h,
                    message_h=message_h,
                    d_fields=d_fields)
            for track in self.tracks:
                orb_md = getattr(track, ORB_METADATA_H)
                if message_h in orb_md.consumes:
                    fn = getattr(track, rname)
                    try:
                        fn(**d_fields)
                    except SolentQuitException:
                        raise
                    except:
                        log('')
                        log('!! breaking in orb [%s], track, %s:%s'%(
                            self.spin_h, track.__class__.__name__, rname))
                        log('')
                        raise
            for cog in self.cogs:
                orb_md = getattr(cog, ORB_METADATA_H)
                if message_h in orb_md.consumes:
                    fn = getattr(cog, rname)
                    try:
                        fn(**d_fields)
                    except SolentQuitException:
                        raise
                    except:
                        log('')
                        log('!! breaking in orb[%s], cog, %s:%s'%(
                            self.spin_h, cog.cog_h, rname))
                        log('')
                        raise
    def cycle(self, max_turns=20):
        '''
        This is useful for testing. It keeps calling orb_turn until there
        is no more activity left to do. You probably do not want an engine
        using this behaviour, because it would lead to starvation of other
        orbs.
        '''
        turn_counter = 0
        activity = activity_new()
        while True:
            log('xxx print %s'%(self.spin_h))
            self.eng_turn(
                activity=activity)
            if activity.get():
                # clears, and then we do another circuit of the while loop
                activity.clear()
            else:
                break
            if max_turns != None and turn_counter >= max_turns:
                log('breaking orb.cycle (reached maxturns %s)'%(
                    max_turns))
                break
            turn_counter += 1
    #
    def _add_cog(self, cog):
        if cog in self.cogs:
            try:
                name = cog.cog_h
            except:
                name = 'unknown, has no cog_h'
            raise Exception("Cog %s is already added."%(name))
        #
        # validate the cog's on_methods match the schema
        cog_h = cog.cog_h
        on_methods = [m for m in dir(cog) if m.startswith('on_')]
        for om_name in on_methods:
            method = getattr(cog, om_name)
            args = inspect.getargspec(method).args
            if args[0] != 'self':
                raise Exception("cog method %s should have arg 'self'."%(
                    om_name))
            args = args[1:]
            message_h = om_name[3:]
            if not self.nearcast_schema.has_message(message_h):
                m = "Cog has %s but there is no message %s in schema."%(
                    om_name, message_h)
                raise Exception(m)
            desired_args = self.nearcast_schema.get_args_for_message(
                message_h=message_h)
            if desired_args != args:
                sb = [ "Nearcast schema message [%s]"%(message_h)
                     , "has fields [%s]."%(', '.join(desired_args))
                     , "%s:%s"%(cog_h, om_name)
                     , "fields are inconsistent: [%s]"%(', '.join(args))
                     ]
                raise Exception(' '.join(sb))
        #
        # validate against easily-made stupid errors
        if 'eng_turn' in dir(cog):
            raise Exception("Use orb_turn, not eng_turn. (%s)"%(
                str(cog)))
        if 'eng_close' in dir(cog):
            raise Exception("Use orb_close, not eng_close. (%s)"%(
                str(cog)))
        #
        install_orb_metadata(cog)
        #
        self.nearcast_schema.attach_nearcast_dispatcher_on_cog(
            orb=self,
            cog=cog)
        self.cogs.append(cog)

def orb_new(spin_h, engine, i_nearcast):
    ob = Orb(
        spin_h=spin_h,
        engine=engine,
        i_nearcast=i_nearcast)
    return ob

