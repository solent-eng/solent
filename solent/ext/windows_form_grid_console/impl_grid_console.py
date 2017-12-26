from solent.forms import FormGridConsole

from solent import init_ext_fn
from solent import hexdump_bytes
from solent import load_clib
from solent import log
from solent import ns
from solent import SolentQuitException

from ctypes import c_char_p
from ctypes import c_int
from ctypes import c_ulong
from ctypes import c_void_p
from ctypes import pointer
import ctypes
import struct

c_ulong_p = ctypes.POINTER(ctypes.c_ulong)

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
        self.event = c_ulong()
        self.ptr_event = c_ulong_p(self.event)
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
        log('turn')
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
            (b0, b1, b2, b3) = struct.unpack('bbbb', self.event)
            log('%s|%s|%s|%s'%(b0, b1, b2, b3))
            if b0 == 0:
                b_another = False
                continue
            else:
                activity.mark(
                    l=self,
                    s='handling input')
                if b0 == 1:
                    # kevent
                    k = b1
                    #
                    zero_h = self.spin_h
                    self.call_windows_event_kevent(
                        zero_h=zero_h,
                        k=k)
                else:
                    raise Exception('unhandled leading byte |%s|'%(b0))
    def eng_close(self):
        log('eng_close')

class ImplGridConsole:
    def __init__(self):
        self.form = FormGridConsole(self)
        #
        clib = load_clib(self)
        #
        self.api = ns()
        self.api.create_screen = init_ext_fn(
            None, clib.create_screen, [c_int, c_int])
        self.api.process_windows_events = init_ext_fn(
            c_int, clib.process_windows_events, [])
        self.api.get_next_event = init_ext_fn(
            None, clib.get_next_event, [c_ulong_p])
        self.api.set = init_ext_fn(
            None, clib.set, [])
        self.api.redraw = init_ext_fn(
            None, clib.redraw, [])
        self.api.close = init_ext_fn(
            None, clib.close, [])
    def zero(self, zero_h, cb_grid_console_splat, cb_grid_console_resize, cb_grid_console_kevent, cb_grid_console_mevent, cb_grid_console_closed, engine, width, height):
        self.zero_h = zero_h
        self.cb_grid_console_splat = cb_grid_console_splat
        self.cb_grid_console_resize = cb_grid_console_resize
        self.cb_grid_console_kevent = cb_grid_console_kevent
        self.cb_grid_console_mevent = cb_grid_console_mevent
        self.cb_grid_console_closed = cb_grid_console_closed
        self.engine = engine
        self.width = width
        self.height = height
        #
        log('before')
        self.api.create_screen(
            width=self.width,
            height=self.height)
        self.api.process_windows_events()
        log('after')
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
    def set(self, cgrid):
        log('get_grid_display')
        raise Exception('nyi')
        #return self.api.set
    def redraw(self):
        log('screen_update')
        return self.api.redraw()
    def close(self):
        log('close')
        return self.api.close()

