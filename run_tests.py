#!/usr/bin/env python3

from testing.libtest import clear_tests
from testing.libtest import have_tests
from testing.libtest import run_tests

import os
import sys

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
TESTING = os.sep.join( [BASE_DIR, 'testing'] )

def test_package(package):
    clear_tests()
    m = __import__(package)
    if have_tests():
        print('#')
        print('# %s'%package)
        print('#')
        run_tests()

def main():
    packages = []
    for tpl in os.walk(TESTING):
        (dname, dirs, filenames) = tpl
        reld = dname[len(BASE_DIR)+1:]
        #
        for fname in filenames:
            if not fname.endswith('.py'):
                continue
            path = os.sep.join( [reld, fname[:-3]] )
            package = '.'.join(path.split(os.sep))
            packages.append(package)
    packages.sort()
    #
    for package in packages:
        test_package(
            package=package)

if __name__ == '__main__':
    main()

'''
for script_name in $(find testing -name "[0-9A-Za-z]*.py" | grep -v '__'); do
    python3 $script_name
    if [[ "$?" != "0" ]]; then
        echo ""
        echo "(run_tests: something looks wrong, making early exit.)"
        echo ""
        exit 1
    fi
done
'''



