#!/usr/bin/env python3

from solent.test import clear_tests
from solent.test import have_tests
from solent.test import run_tests

import os
import sys

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
TESTING = os.sep.join( [BASE_DIR, 'testing'] )

def test_package(package):
    clear_tests()
    try:
        m = __import__(package)
    except:
        print('%s'%package)
        print('-'*(len(package)))
        print('** Could not import')
        raise
    if have_tests():
        print('%s'%package)
        print('-'*(len(package)))
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

