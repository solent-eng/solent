from solent.forms import FormGridConsole

from solent import init_ext_fn
from solent import load_clib
from solent import log
from solent import ns
from solent import SolentQuitException
from solent import e_keycode
from solent.console import Cgrid

from ctypes import c_char_p
from ctypes import c_int
from ctypes import c_uint64
from ctypes import c_void_p
from ctypes import pointer
import ctypes
import struct

c_uint8 = ctypes.c_uint8
c_uint32 = ctypes.c_uint32
c_uint64 = ctypes.c_uint64

c_uint32_p = ctypes.POINTER(c_uint32)
c_uint64_p = ctypes.POINTER(c_uint64)

class SpinWindowsEvents:
    def __init__(self, spin_h, engine, cb_windows_event_quit, cb_windows_event_kevent, api):
        self.spin_h = spin_h
        self.engine = engine
        self.cb_windows_event_quit = cb_windows_event_quit
        self.cb_windows_event_kevent = cb_windows_event_kevent
        self.api = api
        #
        self.cs_windows_event_quit = ns()
        self.cs_windows_event_kevent = ns()
        self.event = c_uint64()
        self.ptr_event = c_uint64_p(self.event)
    def call_windows_event_quit(self, zero_h):
        self.cs_windows_event_quit.zero_h = zero_h
        self.cb_windows_event_quit(
            cs_windows_event_quit=self.cs_windows_event_quit)
    def call_windows_event_kevent(self, zero_h, k):
        self.cs_windows_event_kevent.zero_h = zero_h
        self.cs_windows_event_kevent.k = k
        self.cb_windows_event_kevent(
            cs_windows_event_kevent=self.cs_windows_event_kevent)
    def eng_turn(self, activity):
        #log('turn') # xxx
        #
        b_keep_running = self.api.process_windows_events()
        if not b_keep_running:
            activity.mark(
                l=self,
                s='received quit event')
            #
            zero_h = self.spin_h
            self.call_windows_event_quit(
                zero_h=zero_h)
        #
        b_another = True
        while b_another:
            self.api.get_next_event(self.ptr_event)
            (b0, b1, b2, b3, b4, b5, b6, b7) = struct.unpack(
                'bbbbbbbb', self.event)
            if b0 == 0:
                # Setting b0 to 0 is the API's way of communicating to
                # us that there are no characters to consume.
                b_another = False
                continue
            #
            activity.mark(
                l=self,
                s='handling input')
            log('%s|%s|%s|%s|%s|%s|%s|%s'%(
                b0, b1, b2, b3, b4, b5, b6, b7))
            if b0 == 1:
                # Keystroke event. In this section we will translate [the
                # uint64_t that the api supplied] to a [solent-convention
                # keystroke enumeration that is suitable for the callback.]
                #
                # byte1: bitfield
                ks_bitfield = b1
                # byte2: windows-convention keystroke code that appeared in
                # a WM_KEYDOWN wParam.
                wink = b2
                #
                # unpack the bitfield into values we understand
                b_shift = False
                b_control = False
                n = 128
                if ks_bitfield >= n:
                    ks_bitfield -= n
                    log("Warning. Unhandled bitfield value %s."%n)
                n = 64
                if ks_bitfield >= n:
                    ks_bitfield -= n
                    log("Warning. Unhandled bitfield value %s."%n)
                n = 32
                if ks_bitfield >= n:
                    ks_bitfield -= n
                    log("Warning. Unhandled bitfield value %s."%n)
                n = 16
                if ks_bitfield >= n:
                    ks_bitfield -= n
                    log("Warning. Unhandled bitfield value %s."%n)
                n = 8
                if ks_bitfield >= n:
                    ks_bitfield -= n
                    log("Warning. Unhandled bitfield value %s."%n)
                n = 4
                if ks_bitfield >= n:
                    ks_bitfield -= n
                    log("Warning. Unhandled bitfield value %s."%n)
                n = 2
                if ks_bitfield >= n:
                    ks_bitfield -= n
                    b_control = True
                n = 1
                if ks_bitfield >= n:
                    ks_bitfield -= n
                    b_shift = True
                #
                # arrow handling
                # 0-9 handling
                if wink >= 48 and wink <= 57:
                    # Source character relative to zero
                    zero_offset = wink - 48
                    # xxx Concerns:
                    # - We have no handling for ctrl+numbers at the moment. We
                    #   will want to add this in the future, but needs more
                    #   thought about what codes these translate to. At the
                    #   time of writing, I am tempted to have extension
                    #   characters that pop out the end of the 7-bit ascii
                    #   range, and into the second half of the 8-bit ascii
                    #   range. Mouseclicks could be relocated into this space.
                    # - We are not handling shift+numbers correctly here
                    #   either. There is an awkward keyboard-i18n angle to
                    #   this. For example, shift+2 means different things
                    #   between us-english and uk-english keyboards. Maybe
                    #   we will need to have the C API convey several bytes
                    #   through to us, representing different keycode
                    #   interpretations.
                    n = e_keycode.n0.value + zero_offset
                    #
                    k = e_keycode(n)
                # a-z handling
                elif wink >= 65 and wink <= 90:
                    # Source character relative to lower-case a
                    a_offset = wink - 65
                    if b_control:
                        n = e_keycode.lmousedown.value + a_offset
                    elif b_shift:
                        n = e_keycode.A.value + a_offset
                    else:
                        # Lower A is 97
                        n = e_keycode.a.value + a_offset
                    k = e_keycode(n)
                else:
                    # xxx
                    log("Unhandled %s"%(wink))
                    n = wink
                    #
                    k = e_keycode(n)
                #
                zero_h = self.spin_h
                self.call_windows_event_kevent(
                    zero_h=zero_h,
                    k=k)
            else:
                raise Exception('unhandled leading byte |%s|'%(b0))
    def eng_close(self):
        log('eng_close')

# ctypes magic to allow the C layer to call-back to our python layer. The 'ca'
# form here is like a callback, but takes explicit arguments rather than a
# callback structure.
CC_LOG_T = ctypes.WINFUNCTYPE(None, ctypes.c_char_p)

def ca_log(msg):
    s = msg.decode('utf8')
    log("[ca_log] %s"%(s))

cc_log = CC_LOG_T(ca_log)

class ImplGridConsole:
    def __init__(self):
        self.form = FormGridConsole(self)
        #
        clib = load_clib(self)
        #
        self.api = ns()
        self.api.set_cc_log = init_ext_fn(
            None, clib.set_cc_log, [CC_LOG_T])
        self.api.create_screen = init_ext_fn(
            None, clib.create_screen, [c_int, c_int])
        self.api.process_windows_events = init_ext_fn(
            c_int, clib.process_windows_events, [])
        self.api.get_next_event = init_ext_fn(
            None, clib.get_next_event, [c_uint64_p])
        self.api.set = init_ext_fn(
            None, clib.set, [c_int, c_int, c_int, c_int])
        self.api.redraw = init_ext_fn(
            None, clib.redraw, [])
        self.api.close = init_ext_fn(
            None, clib.close, [])
    def zero(self, zero_h, cb_grid_console_splat, cb_grid_console_kevent, cb_grid_console_mevent, cb_grid_console_closed, engine, width, height):
        self.zero_h = zero_h
        self.cb_grid_console_splat = cb_grid_console_splat
        self.cb_grid_console_kevent = cb_grid_console_kevent
        self.cb_grid_console_mevent = cb_grid_console_mevent
        self.cb_grid_console_closed = cb_grid_console_closed
        self.engine = engine
        self.width = width
        self.height = height
        #
        if self.width > 200 or self.height > 100:
            # Note that width and height are by character, not by screen
            # dimension.
            log("Warning. Have seen crashes as screen dimensions become vast.")
            log('width %s %s'%(self.width, type(self.width)))
            log('height %s %s'%(self.height, type(self.height)))
        #
        self.cgrid = Cgrid(
            width=width,
            height=height)
        #
        # Emphasis: do not use named parameters for this, or the variable
        # holding the logger will get garbage-collected. You must directly
        # refer to cc_log.
        # xxx rename api to c_api
        self.api.set_cc_log(cc_log)
        #
        log('impl_grid_console w:%s h:%s'%(self.width, self.height))
        self.api.create_screen(self.width, self.height)
        self.api.process_windows_events()
        #
        self.spin_windows_events = self.engine.init_spin(
            construct=SpinWindowsEvents,
            cb_windows_event_quit=self.cb_windows_event_quit,
            cb_windows_event_kevent=self.cb_windows_event_kevent,
            api=self.api)
    def cb_windows_event_quit(self, cs_windows_event_quit):
        zero_h = cs_windows_event_quit.zero_h
        #
        raise SolentQuitException()
    def cb_windows_event_kevent(self, cs_windows_event_kevent):
        zero_h = cs_windows_event_kevent.zero_h
        k = cs_windows_event_kevent.k
        #
        # xxx we will need to do some translation here from windows-style
        # keycodes to solent style. for the moment I am just passing back the
        # raw values.
        keycode = k
        self.form.call_grid_console_kevent(
            zero_h=self.zero_h,
            keycode=keycode)
    #
    def send(self, cgrid):
        cur_dim = (self.cgrid.width, self.cgrid.height)
        new_dim = (cgrid.width, cgrid.height)
        if cur_dim != new_dim:
            self.cgrid.set_dimensions(
                width=cgrid.width,
                height=cgrid.height)
        updates = []
        o_spots = self.cgrid.spots
        n_spots = cgrid.spots
        for cgrid_idx, (o_spot, n_spot) in enumerate(zip(o_spots, n_spots)):
            if not o_spot.compare(n_spot):
                updates.append(cgrid_idx)
                o_spot.mimic(n_spot)
        log('send')
        for cgrid_idx in updates:
            spot = self.cgrid.spots[cgrid_idx]
            #
            drop = int(cgrid_idx/self.cgrid.width)
            rest = int(cgrid_idx%self.cgrid.width)
            c = ord(spot.c)
            o = 0 # xxx
            log('update %s %s %s %s'%(drop, rest, c, o))
            self.api.set(drop, rest, c, o)
        self.api.redraw()
    def close(self):
        log('close')
        return self.api.close()

