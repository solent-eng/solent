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

from solent import Engine
from solent import hexdump
from solent import log
from solent import SolentQuitException

import os
import sys

def read_file_binary(fname):
    f_ptr = open(fname, 'rb')
    bb = f_ptr.read()
    f_ptr.close()
    return bb

def usage(ecode=1):
    print('Usage:')
    print('  %s FILENAME'%(sys.argv[0]))
    sys.exit(ecode)

def validate_filename(fname):
    if not os.path.exists(fname):
        print("ERROR: no file at %s"%(fname))
        sys.exit(1)
    #
    if not os.path.isfile(fname):
        print("ERROR: no file at %s"%(fname))
        sys.exit(1)

def main():
    if '--help' in sys.argv:
        usage(0)
    if 2 != len(sys.argv):
        usage()
    #
    fname = sys.argv[1]
    validate_filename(
        fname=fname)
    #
    bb = read_file_binary(fname)
    print('len %s'%len(bb))
    hexdump(
        bb=bb,
        title=fname)

if __name__ == '__main__':
    main()

