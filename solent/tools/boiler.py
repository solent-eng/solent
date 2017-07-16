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
# // overview
# This is easier to understand by seeing it than explaining it.
#
# Attempt to explain:
# You can drop the text from a callback struct in here. Each time you do,
# this will give you stencils you might require for other parts of the
# program.
#
# Show you:
# Copy a definition of a call struct into your clipboard. For example, grab
# CsRcpFound below. Run this program. Paste your clipboard into the console.
#
# Why this is useful:
# There is a bunch of boilerplate work involved in putting solent systems
# together. This makes the boilerplate easy.

from solent import uniq

import re


# --------------------------------------------------------
#   util
# --------------------------------------------------------
def convert_camel_to_snake(name):
    '''from
    https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    '''
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


# --------------------------------------------------------
#   cs parser
# --------------------------------------------------------
class CsRcpError:
    def __init__(self):
        self.msg = None

class CsRcpFound:
    def __init__(self):
        self.cname = None
        self.fields = None

RCP_MODE_EXPECT_CLASS_LINE = uniq()
RCP_MODE_EXPECT_INIT_LINE = uniq()
RCP_MODE_EXPECT_FIELD_OR_TERM = uniq()

PATTERN_CLINE = re.compile('^ *class Cs[a-zA-Z0-9]*:$')
PATTERN_COMMENT = re.compile('^ *#')
PATTERN_STRING = re.compile('^ *"')
PATTERN_INIT = re.compile('^ *def __init__\(self\):$')
PATTERN_FIELD = re.compile('^ *self.[a-z0-9_]* = None$')

class RailCsParser:
    def __init__(self):
        self.cs_rcp_error = CsRcpError()
        self.cs_rcp_found = CsRcpFound()
    def zero(self, cb_rcp_error, cb_rcp_found):
        self.cb_rcp_error = cb_rcp_error
        self.cb_rcp_found = cb_rcp_found
        #
        self._reset()
    def _reset(self):
        self.mode = RCP_MODE_EXPECT_CLASS_LINE
        self.cname = None
        self.fields = []
    #
    def accept(self, line):
        if self.mode == RCP_MODE_EXPECT_CLASS_LINE:
            if line.strip() == '':
                return
            if None == PATTERN_CLINE.match(line):
                self._error_and_reset("weird line [%s]"%(
                    line))
                return
            #
            cs_name = line.split(' ')[-1].split(':')[0]
            self.cname = convert_camel_to_snake(
                name=cs_name[2:])
            self.mode = RCP_MODE_EXPECT_INIT_LINE
        elif self.mode == RCP_MODE_EXPECT_INIT_LINE:
            if PATTERN_COMMENT.match(line):
                # That's fine.
                return
            if PATTERN_STRING.match(line):
                # That's fine. Although: we are not handling the multi-line
                # scenario here. If this becomes a significant tool we can do
                # that later.
                return
            if not PATTERN_INIT.match(line):
                self._error_and_reset(
                    msg='Expected init line. Instead got |%s|'%(
                        line))
                return
            self.mode = RCP_MODE_EXPECT_FIELD_OR_TERM
        elif self.mode == RCP_MODE_EXPECT_FIELD_OR_TERM:
            if line.strip() == '':
                self._end_block()
            elif PATTERN_FIELD.match(line):
                field = line.split('self.')[1].split(' ')[0]
                self.fields.append(field)
            else:
                self._error_and_reset(
                    msg='weird line |%s|'%(line))
        else:
            raise Exception("unknown mode %s"%(self.mode))
    #
    def _call_rcp_error(self, msg):
        self.cs_rcp_error.msg = msg
        self.cb_rcp_error(
            cs_rcp_error=self.cs_rcp_error)
    def _call_rcp_found(self, cname, fields):
        self.cs_rcp_found.cname = cname
        self.cs_rcp_found.fields = fields
        self.cb_rcp_found(
            cs_rcp_found=self.cs_rcp_found)
    #
    def _error_and_reset(self, msg):
        self._call_rcp_error(
            msg=msg)
        self._reset()
    def _end_block(self):
        self._call_rcp_found(
            cname=self.cname,
            fields=self.fields)
        #
        self.cname = None
        self.fields = []
        self.mode = RCP_MODE_EXPECT_CLASS_LINE


# --------------------------------------------------------
#   renders
# --------------------------------------------------------
def render_call_function(cname, fields):
    sb = []
    sb.append('    ')
    sb.append('def _call_%s(self'%cname)
    for f in fields:
        sb.append(', %s'%(f))
    sb.append('):')
    sb.append('\n')
    for f in fields:
        sb.append('        ')
        sb.append('self.cs_%s.%s = %s'%(
            cname, f, f))
        sb.append('\n')
    sb.append('        ')
    sb.append('self.cb_%s('%(cname))
    sb.append('\n')
    sb.append('            ')
    sb.append('cs_%s=self.cs_%s)'%(
        cname, cname))
    sb.append('\n')
    print(''.join(sb))

def render_callback_def(cname, fields):
    sb = []
    sb.append('    ')
    sb.append('def cb_%s(self, cs_%s):'%(cname, cname))
    sb.append('\n')
    for f in fields:
        sb.append('        ')
        sb.append('%s = cs_%s.%s'%(f, cname, f))
        sb.append('\n')
    sb.append('        ')
    sb.append('#')
    sb.append('\n')
    sb.append('        ')
    sb.append("log('xxx cb_%s')"%(cname))
    sb.append('\n')
    print(''.join(sb))


# --------------------------------------------------------
#   launch
# --------------------------------------------------------
def cb_rcp_error(cs_rcp_error):
    msg = cs_rcp_error.msg
    #
    print("ERROR: %s"%msg)

def cb_rcp_found(cs_rcp_found):
    cname = cs_rcp_found.cname
    fields = cs_rcp_found.fields
    #
    print('--------------------------------------------------------')
    render_call_function(
        cname=cname,
        fields=fields)
    render_callback_def(
        cname=cname,
        fields=fields)
    print('--------------------------------------------------------')

def app():
    rail_cs_parser = RailCsParser()
    rail_cs_parser.zero(
        cb_rcp_error=cb_rcp_error,
        cb_rcp_found=cb_rcp_found)
    print('** Paste call struct class definitions in here.')
    while True:
        line = input()
        rail_cs_parser.accept(
            line=line)

def main():
    try:
        app()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()

