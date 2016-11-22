#
# interface script
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

from solent.util.line_finder import line_finder_new

import inspect

def parse_line_to_tokens(line):
    tokens = []
    acc = []
    def esc_append(c):
        if c == '\n':
            pass
        else:
            acc.append(c)
    mode_normal   = 0
    mode_squotes  = 1
    mode_dquotes  = 2
    mode_escape_n = 3 # escape, normal mode
    mode_escape_s = 4 # escape, single-quote mode
    mode_escape_d = 5 # escape, double-quote mode
    var_mode = [mode_normal]
    def set_mode(m):
        var_mode[0] = m
    def mode():
        return var_mode[0]
    def spin(force=False):
        s = ''.join(acc).strip()
        if force or s: tokens.append(s)
        while acc: acc.pop()
        var_mode[0] = mode_normal
    for c in line.strip():
        if mode() == mode_escape_n:
            esc_append(c)
            set_mode(mode_normal)
        elif mode() == mode_escape_s:
            esc_append(c)
            set_mode(mode_squotes)
        elif mode() == mode_escape_d:
            esc_append(c)
            set_mode(mode_dquotes)
        elif mode() == mode_normal:
            if c == '\\':
                set_mode(mode_escape_n)
            elif c == ' ':
                # end of word
                spin()
            elif c == '#':
                # comment
                spin()
                break
            elif c == '"':
                # enter double quotes
                spin()
                set_mode(mode_dquotes)
            elif c == "'":
                # enter single quotes
                spin()
                set_mode(mode_squotes)
            else:
                acc.append(c)
        elif mode() == mode_squotes:
            if c == '\\':
                set_mode(mode_escape_s)
            elif c == "'":
                # exit single quotes
                spin(True)
            else:
                acc.append(c)
        elif mode() == mode_dquotes:
            if c == '\\':
                set_mode(mode_escape_d)
            elif c == '"':
                # exit double quotes
                spin(True)
            else:
                acc.append(c)
        else:
            raise Exception('Should not get here [%s]'%mode())
    if mode() != mode_normal:
        raise Exception("invalid line. [%s]"%(line))
    spin()
    return tokens

class InterfaceScriptParser(object):
    def __init__(self, cb_interface, cb_signal):
        # on_interface(iname, vfields) -> None
        self.cb_interface = cb_interface
        # on_signal(iname, values) -> None
        self.cb_signal = cb_signal
        #
        self.finder = line_finder_new(
            cb_line=self._on_line)
        self.interfaces = {}
    def parse(self, s):
        self.finder.accept_string(
			s=s)
    def _on_line(self, line):
        tokens = parse_line_to_tokens(line)
        if not tokens:
            return
        if tokens[0] == 'i':
            self._handle_interface(tokens)
        else:
            if tokens[0] == '.':
                tokens = tokens[1:]
            self._handle_signal(tokens)
    def _handle_interface(self, tokens):
        if len(tokens) < 2:
            raise Exception("Invalid vdef %s"%str(tokens))
        iname = tokens[1]
        vfields = tokens[2:]
        if iname in self.interfaces:
            # it's fine to have multiple definitions, but they must
            # be consistent.
            current = self.interfaces[iname]
            if vfields != current:
                m = "inconsistent vdefs %s %s"%(
                    str(current),
                    str(vfields))
                raise Exception(m)
        else:
            self.interfaces[iname] = vfields
            self.cb_interface(iname, vfields)
    def _handle_signal(self, tokens):
        iname = tokens[0]
        if iname not in self.interfaces:
            raise Exception("no interface defined for %s"%iname)
        vfields = self.interfaces[iname]
        values = tokens[1:]
        if len(vfields) != len(values):
            raise Exception("wrong number of args. i %s %s. got %s"%(
                iname, str(vfields), str(values)))
        self.cb_signal(iname, values)

class SignalConsumer(object):
    def on_interface(self, iname, vfields):
        method_name = 'on_%s'%iname
        if method_name not in dir(self):
            raise Exception('no handler [%s]'%method_name)
        method = getattr(self, method_name)
        argspec = inspect.getargspec(method)[0][1:]
        if argspec != vfields:
            raise Exception('inconsistent spec for %s got:%s method:%s'%(
                iname, str(argspec), str(vfields)))
    def on_signal(self, iname, values):
        method_name = 'on_%s'%iname
        if method_name not in dir(self):
            raise Exception('no handler [%s]'%method_name)
        method = getattr(self, method_name)
        method(*values)

# sample
class SampleApp(SignalConsumer):
    def on_node(self, nid, t_deployment, t_outpost_codebase):
        print('node %s'%nid)
    def on_orb(self, module, instance_h):
        print('orb %s %s'%(module, instance_h))
    def on_kv(self, key, value):
        print('kv %s %s'%(key, value))

def init_interface_script_parser(signal_consumer):
    ob = InterfaceScriptParser(
        cb_interface=signal_consumer.on_interface,
        cb_signal=signal_consumer.on_signal)
    return ob


