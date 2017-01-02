#
# setup.py
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

from setuptools import setup
from setuptools import find_packages

import os
import sys


def check_python_version():
    if sys.version_info.major < 3:
        print('''
          I'm only for python 3. There is a version of the eng networking
          library maintained for python 2, but it's not offered through pip
          at the moment. Check it out at github.com/cratuki/eng. If you get
          into trouble, feel free to contact me using (github username) at
          (google mail service) dot com.
        ''')
        sys.exit(1)


def main():
    check_python_version()

    solent_packages = sorted([pname for pname in find_packages() if (
        pname == 'solent' or pname.startswith('solent.'))])

    setup(
        name='solent',
        packages=solent_packages,
        version='0.21',
        description='Event-driven concurrency engine',
        url='https://github.com/cratuki/solent',
        download_url='https://github.com/cratuki/solent/tarball/0.21',
        keywords=[
            'solent',
            'eng',
            'term',
            'networking',
            'roguelikes',
            'async'],
        classifiers=[],
        include_package_data=True,
    )

if __name__ == '__main__':
    main()
