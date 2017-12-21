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
# Demonstrate network logging, particularly with long lines. To see this
# logging on the wire, run udpcat,
#   python3 -B -m solent.tools.udpcat 127.255.255.255 7789

from solent import init_network_logging
from solent import log

import sys

MTU = 30
ADDR = '127.255.255.255'
PORT = 7789

def main():
    init_network_logging(
        mtu=MTU,
        addr=ADDR,
        port=PORT,
        label="solent.draft.network_logging")
    #
    # Simple short line
    log('')
    log('|short|short')
    log('.')
    #
    # Longer-than-MTU line
    log('')
    log('|longer-than-mtu|hijklmnopqrstuvwzyx')
    log('.')
    #
    # Exactly-one-MTU line
    log('')
    log('|one-mtu|jklmnopqrstuvwzyx0123')
    log('.')
    #
    # Exactly-two-MTU line
    log('')
    log('|two-mtu|jklmnopqrstuvwzyx0123abcdefghijklmnopqrstuvwzyx0123')
    log('.')

if __name__ == '__main__':
    main()

