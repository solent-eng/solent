from solent import log

import importlib
import os

MAGIC_NAME_FOR_BUILD_PY = 'build.py'

def dyn_import(pkg):
    log('pname %s'%pname)
    m = importlib.import_module(pname)
    return m

def main():
    for (relpath, subdirs, files) in sorted(os.walk('wsrc')):
        if MAGIC_NAME_FOR_BUILD_PY in files:
            print()
            print(f"** {relpath}")
            print()

            package = '.'.join(relpath.split(os.sep))
            build_within_package = MAGIC_NAME_FOR_BUILD_PY[:-3]
            pname = '%s.%s'%(package, build_within_package)
            log('')
            log('  [%s]'%(pname))
            log('')
            build_m = importlib.import_module(pname)
            build_m.main()

if __name__ == '__main__':
    main()

