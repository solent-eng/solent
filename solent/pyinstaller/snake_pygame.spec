# -*- mode: python -*-
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

from solent import dget_root
from solent.pyinstaller import add_resource_from_relpath

import os

DIST_NAME = 'snake_pygame'
LAUNCH_RELPATH = 'solent/pyinstaller/launch/snake/snake_pygame.py'

def pyinstaller_block():
    '''
    The contents of this function has been adapted from a spec file generated
    by pyinstaller. Usage was:

    pyinstaller --onefile --windowed solent/pyinstaller/launch/snake/snake_pygame.py
    '''
    root_dir = dget_root()
    os.chdir(root_dir)
    #
    python_launcher = os.sep.join([root_dir, LAUNCH_RELPATH])
    # Keep these as relative paths (see add_resource_from_relpath)
    other_resource_directories = [
        'static',
        'wres']
    #
    block_cipher = None
    a = Analysis([python_launcher],
                 pathex=[root_dir],
                 binaries=None,
                 datas=[],
                 hiddenimports=[],
                 hookspath=[],
                 runtime_hooks=[],
                 excludes=[],
                 win_no_prefer_redirects=False,
                 win_private_assemblies=False,
                 cipher=block_cipher)
    for rdir in other_resource_directories:
        a.datas += add_resource_from_relpath(rdir)
    pyz = PYZ(a.pure, a.zipped_data,
                 cipher=block_cipher)
    exe = EXE(pyz,
              a.scripts,
              a.binaries,
              a.zipfiles,
              a.datas,
              name=DIST_NAME,
              debug=False,
              strip=False,
              upx=True,
              console=False )

# This needs to be at the root level like this, and not launched from the
# ususal 'if name is main' arrangement. pyinstaller will run this module.
pyinstaller_block()

