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
# This should only be used by unit tests. And you probably never want to
# construct it directly. Rather, use orb:init_testbridge.
#
# The function init_testbridge_class inspects a nearcast schema, and uses
# this information to dynamically create a cog. The cog it creates will listen
# to everything on the nearcast, and give you handy methods for interacting
# with it. For each nearcast message defined in the schema, this class will
# expose these methods:
#
#   count_mname
#       returns the number of mname messages seen on the nearcast
#
#   get_mname
#       returns all the messages of type mname seen on the nearcast
#
#   last_mname
#       returns the last mname message seen on the nearcast
#
#   log_mname
#       logs all the mname messages seen so far
#
#   on_mname
#       this is the method that receives mname messages as they arrive
#
#   nc_mname
#       easy mechanism for sending aa mname message to the nearcast
#
# See testing/lconsole/spin_line_console.py for an example of this being
# used in anger.

from solent import Ns
from solent import log

import os
import random
from string import Template
import shutil
import sys
import time

T_HEADING = Template('''#
# (!) this file is generated by testbridge.py
#

from solent import log

class TestBridgeCog:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
$declare_acc_variables
$function_lines

''')

T_FUNCTIONS_FOR_MESSAGES_WITH_FIELDS = Template('''    #
    def count_$mname(self):
        return len(self.acc_$mname)
    def get_$mname(self):
        return self.acc_$mname
    def last_$mname(self):
        return self.acc_$mname[-1]
    def log_$mname(self):
        for l in self.acc_$mname:
            log(l)
    def on_$mname(self, $csep_fields):
        self.acc_$mname.append( ($csep_fields,) )
    def nc_$mname(self, $csep_fields):
        self.orb.nearcast(
            cog=self,
            message_h='$mname',
$equals_bits)
        self.orb.cycle()''')

T_FUNCTIONS_FOR_MESSAGES_WITH_NO_FIELDS = Template('''    #
    def on_$mname(self):
        self.acc_$mname.append(None)
    def count_$mname(self):
        return len(self.acc_$mname)
    def get_$mname(self):
        return self.acc_$mname
    def last_$mname(self):
        return self.acc_$mname[-1]
    def log_$mname(self):
        for l in self.acc_$mname:
            log(l)
    def nc_$mname(self):
        self.orb.nearcast(
            cog=self,
            message_h='$mname')
        self.orb.cycle()''')

def create_code_file_and_then_dynamically_import_class(code):
    dname = '/tmp/solent.testing.%s.%s'%(
        str(time.time()), str(random.random()))
    if os.path.exists(dname):
        # paranoid, because there is a shutil.rmtree below
        raise Exception("very weird")
    else:
        os.mkdir(dname)
    fname = os.sep.join( [dname, 'dyn_receiver_cog.py'] )
    f_ptr = open(fname, 'w+')
    f_ptr.write(code)
    f_ptr.close()
    #
    # import
    sys.path.append(dname)
    import dyn_receiver_cog
    TestBridgeCog = dyn_receiver_cog.TestBridgeCog
    #
    # cleanup
    sys.path.pop()
    del dyn_receiver_cog
    os.remove(fname)
    shutil.rmtree(dname)
    #
    # here it is
    return TestBridgeCog

def init_testbridge_class(nearcast_schema):
    #
    # Harvest the nearcast schema to synthesise a class with listeners
    # for its messages, and ability to nearcast to it.
    acc_lines = []
    for mname in nearcast_schema.messages.keys():
        acc_lines.append('        self.acc_%s = []'%(mname))
    #
    rendered_function_blocks = []
    for (mname, fields) in nearcast_schema.messages.items():
        if fields:
            sb_equals_bits = []
            for field in fields:
                sb_equals_bits.append('            %s=%s,'%(field, field))
            block = T_FUNCTIONS_FOR_MESSAGES_WITH_FIELDS.substitute(
                mname=mname,
                csep_fields=', '.join(fields),
                equals_bits='\n'.join(sb_equals_bits))
            rendered_function_blocks.append(block)
        else:
            block = T_FUNCTIONS_FOR_MESSAGES_WITH_NO_FIELDS.substitute(
                mname=mname)
            rendered_function_blocks.append(block)
    #
    code = T_HEADING.substitute(
        declare_acc_variables='\n'.join(acc_lines),
        function_lines='\n'.join(rendered_function_blocks))
    #
    # I found exec to be fiddly. Instead, we are going to create a file with
    # the code in, and dynamically import it.
    TestBridgeCog = create_code_file_and_then_dynamically_import_class(code)
    return TestBridgeCog

