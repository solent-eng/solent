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
from solent import log

import getpass
import os
import platform
import string

def ensure_dir(path):
    if not os.path.exists(path):
        log("Creating %s"%path)
        os.makedirs(path)

def write_file(path, content):
    f_ptr = open(path, 'w+')
    f_ptr.write(content)
    f_ptr.close()

def chmod_plus_x(path):
    os.system('chmod +x %s'%path)

def create_unix_build_script(wsrc_path, wres_path):
    content = string.Template('''
        cd $wsrc_path
        gcc -shared -Wl,-soname,api -o $wres_path/api.so -fPIC api.c
    ''').safe_substitute(
        wsrc_path=wsrc_path,
        wres_path=wres_path)
    path = '/tmp/.%s.solent-build.sh'%getpass.getuser()
    write_file(path, content)
    #
    chmod_plus_x(path)
    #
    return path

def create_windows_build_script(wsrc_path, wres_path):
    content = string.Template(r'''
        @echo off

        rem --------------------------------------------------------------------------
        rem I don't have much experience at developing on Windows. Maybe there is a
        rem way to use something like cmake to allow us to use a single build tool
        rem across platforms. Need to look into this.
        rem --------------------------------------------------------------------------

        set MINGW=c:\Program Files (x86)\CodeBlocks\MinGW
        set PATH=%PATH%;%MINGW%\bin

        cd $wsrc_path

        mingw32-g++ -c -DBUILDING_DLL winplace.c -o obj\winplace.o
        mingw32-g++ -c -DBUILDING_DLL api.c -o obj\api.o
        mingw32-g++ -shared -o $wres_path/api.dll obj\winplace.o obj\api.o -lgdi32 -luser32 -lkernel32 -lcomctl32 -lwinmm -mwindows -Wl,--out-implib,$wres_path/libapi_dll.a
    ''').safe_substitute(
        wsrc_path=wsrc_path,
        wres_path=wres_path)
    path = r'c:\temp\build.bat'
    write_file(path, content)
    #
    return path

def main():
    package_elements = __package__.split('.')
    wsrc_path = dget_root(*package_elements)
    wres_path = dget_wres(*package_elements[1:])
    ensure_dir(wres_path)
    #
    system = platform.system()
    if system == 'Windows':
        path_build_script = create_windows_build_script(
            wsrc_path=wsrc_path,
            wres_path=wres_path)
    else:
        path_build_script = create_unix_build_script(
            wsrc_path=wsrc_path,
            wres_path=wres_path)
    #
    # A better approach would be to explicitly create files and then execute
    # those, probably in a fingerprint directory. Makes for easier debugging.
    # Can do later.
    print(path_build_script)
    os.system(path_build_script)
    log('Should have created api.so in %s'%(wres_path))

if __name__ == '__main__':
    main()

