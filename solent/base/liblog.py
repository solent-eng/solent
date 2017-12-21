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
# Simple wrapper for logging. motive of this is that sometimes you
# want to be able to broadcast logs to the network rather than write to file.
# (yes, udp broadcast is unreliable, but for many applications it's damn
# useful). This library includes functionality that makes that easy.

import logging
import socket
import struct
import sys

LOGGER = None

def outer_exception():
    logging.exception("outer_except")

def log(msg):
    global LOGGER
    if None == LOGGER:
        init_logging()
    LOGGER(str(msg))

def newliney_info(msg):
    if msg.endswith('\n'):
        logging.info(msg[:-1])
    else:
        logging.info(msg)

def init_logging():
    fstring='%(asctime)-15s | %(message)s'
    logging.basicConfig( level=logging.DEBUG
                       , format=fstring
                       , datefmt='%Y%m%d %H:%M.%S'
                       )
    global LOGGER
    LOGGER = newliney_info

class NetLogger:
    def __init__(self, mtu, addr, port, label):
        self.mtu = mtu
        self.addr = addr
        self.port = port
        self.label = label
        #
        # disable nagle
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  
        self.sock.connect((addr, port))
    def send(self, msg):
        if msg.endswith('\n'):
            msg = '[%s] %s'%(self.label, msg)
        else:
            msg = '[%s] %s\n'%(self.label, msg)
        bb = bytes(msg, 'utf8')
        self.sock.send(bb)

def init_network_logging(mtu, addr, port, label):
    global LOGGER
    #
    net_logger = NetLogger(
        mtu=mtu,
        addr=addr,
        port=port,
        label=label)
    LOGGER = net_logger.send

def hexdump_string(s, title='hexdump'):
    int_buffer = []
    for c in s:
        int_buffer.append(ord(c))
    bb = bytearray(int_buffer)
    hexdump_bytes(
        bb=bb,
        title=title)

def hexdump_bytes(bb, title='hexdump'):
    #
    # Awkward implementation of. Mixes up print-as-you-go (for the bytes
    # on the left) with buffer-building (for the displayable characters
    # on the right).
    #
    arr_len = len(bb)
    DOT = ord('.')
    SPACE = ord(' ')
    BAR = ord('|')
    #
    # This is the buffer where we accumulate things to print on the
    # right-hand-side of the buffer (i.e. displayable characters where
    # we can, or a substitute period to represent non-displayable
    # characters)
    acc_rhs_bb = []
    def append_dot():
        acc_rhs_bb.append(DOT)
    def append_bar():
        acc_rhs_bb.append(BAR)
    def append_space():
        acc_rhs_bb.append(SPACE)
    def render_sb():
        print(':::', end=' ')
        print(''.join( [chr(b) for b in acc_rhs_bb] ))
        while acc_rhs_bb: acc_rhs_bb.pop()
    #
    # Heading
    print('// %s [%s bytes]'%(title, arr_len))
    #
    # Main content
    idx = 0
    for (idx, b) in enumerate(bb):
        print('%02x'%(b), end=' ')
        if b >= ord(' ') and b <= ord('~'):
            acc_rhs_bb.append(b)
        else:
            append_dot()
        if (idx+1) % 16 == 0:
            render_sb()
        elif (idx+1) % 8 == 0:
            append_space()
            append_bar()
            append_space()
            print('|', end=' ')
    idx += 1
    #
    # Cleanup on the final line
    if idx % 16 != 0:
        while (idx+1) % 16 != 0:
            print('..', end=' ')
            append_space()
            if (idx+1) % 8 == 0:
                print('|', end=' ')
            idx += 1
        print('..', end=' ')
        render_sb()
    print()

if __name__ == '__main__':
    hexdump_string('abc')

