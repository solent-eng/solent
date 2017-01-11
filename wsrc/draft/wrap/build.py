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

from wsrc import dget_root
from wsrc import dget_wres
from solent.log import log

import os
import string

def ensure_dir(path):
    if not os.path.exists(path):
        log("Creating %s"%path)
        os.makedirs(path)

def main():
    package_elements = __package__.split('.')
    wsrc_path = dget_root(*package_elements)
    wres_path = dget_wres(*package_elements[1:])
    ensure_dir(wres_path)
    build_script = string.Template('''
        cd $wsrc_path
        gcc -shared -Wl,-soname,api -o $wres_path/api.so -fPIC api.c
    ''').safe_substitute(
        wsrc_path=wsrc_path,
        wres_path=wres_path)
    #
    # A better approahc would be to explicitly create files and then execute
    # those, probably in a fingerprint directory. Makes for easier debugging.
    # Can do later.
    os.system(build_script)
    log('Should have created api.so in %s'%(wres_path))

if __name__ == '__main__':
    main()

