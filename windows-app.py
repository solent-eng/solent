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
# This is a development-launcher for Windows. That is, it serves the same
# function as 'app', but for Windows.

import os
import subprocess

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

LAUNCH = "run_tests"
#LAUNCH = "solent.demo.snake"

def read_file(path):
    f_ptr = open(path)
    data = f_ptr.read()
    f_ptr.close()
    return data

def pause():
    print('// paused')
    print('')
    input()

def run(launch):
    venv_python = os.path.join(BASE_DIR, 'venv', 'Scripts', 'python.exe')
    if not os.path.exists(venv_python):
        raise Exception("Assumes venv. (Create venv under the base dir)")
    #
    args = [venv_python, '-B', '-m', launch]
    print(args)
    p = subprocess.Popen(
        args=args,
        cwd=BASE_DIR)
    p.wait()

def main():
    while True:
        path_launch = os.path.join(BASE_DIR, 'windows-app.txt')
        python_mod = [line
            for line
            in read_file(path_launch).split('\n')
            if len(line.strip()) > 0
            and not line.strip().startswith('#')]
        if not python_mod:
            raise Exception("No module enabled in %s"%(path_launch))
        #
        for launch in python_mod:
            print('')
            print(':: %s'%launch)
            run(launch)
            pause()

if __name__ == '__main__':
    main()

