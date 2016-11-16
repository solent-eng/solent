#
# liblog. Simple wrapper for logging. motive of this is that sometimes you
# want to be able to broadcast logs to the network rather than write to file.
# (yes, udp broadcast is unreliable, but for many applications it's damn
# useful). This library includes functionality that makes that easy.
#
#
# --------------------------------------------------------
#   :license
# --------------------------------------------------------
#
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
# .

import logging
import socket
import struct
import sys

LOGGER = None

def outer_exception():
    logging.exception("outer_except")

def log(msg):
    global LOGGER
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

def init_logging_to_udp(addr, port, nid):
    '''
    This initiates logging so that it will do a UDP broadcast of anything that
    comes in. UDP is an unreliable protocol, but for many applications this
    approach will be adequate.
    
    The broadcast message is not just the raw text. Rather, there is a short
    header of a couple of bytes indicating whether the message was from stdout
    or stderr. Look at the fingerprint section below for these values.

    It would probably be easy to adapt to qd_listen as a receiver of these
    messages. I have a more elaborate system hanging around that does this
    already ("orb_ancient_logger") and expect it will get incorporated to the
    solent codebase at some point.
    '''
    #
    # Useful for debugging
    orig_stdout = sys.stdout
    orig_stderr = sys.stderr
    #
    # No metasocks here. We just open a raw broadcast socket in the
    # most liberal way we can.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  
    sock.connect((addr, port))
    #
    class IoHijack(object):
        def __init__(self):
            pass
        def write(self, msg, is_stderr=False):
            def sized_send(sized_s):
                pack = self._encase(sized_s, is_stderr)
                #
                #sys.stdout = orig_stdout
                #nicehex(pack, title='logpack')
                #sys.stdout = io_hijack
                #
                sock.send(pack)
            max_payload_size = CORE_MTU - 8
            msg = '%s\n'%msg
            s = msg
            while len(s) > max_payload_size:
                sized_send(s[:max_payload_size])
                s = s[max_payload_size:]
            sized_send(s)
            #orig_stdout.write(msg)
        def _encase(self, s, is_stderr):
            'Encases a string in the log format. See orb_ancient_logger.'
            sb = []
            #
            # // fingerprint
            if is_stderr:
                sb.append(chr(0x10))
                sb.append(chr(0x6e)) # stderr
            else:
                sb.append(chr(0x10))
                sb.append(chr(0x60)) # stdout
            #
            # // payload size (big-endian)
            sb.extend(struct.pack('!H', len(s)))
            #
            # // node id
            sb.extend(struct.pack('!L', int(nid, 16)))
            #
            # // payload
            sb.extend(s)
            return ''.join(sb)
    io_hijack = IoHijack()
    global LOGGER
    LOGGER = io_hijack.write
    #
    # While you're debugging udp broadcast, it can help to disable this.
    sys.stdout = io_hijack
    class StdErrWrapper(object):
        def __init__(self):
            pass
        def write(self, s):
            io_hijack.write(s, True)
    sys.stderr = StdErrWrapper()

def nicehex(lst_bytes, title='nicehex'):
    print('= %s'%(title))
    sb = []
    def render_sb():
        print(':::', end=' ')
        print(''.join(sb))
        while sb: sb.pop()
    for (idx, c) in enumerate(lst_bytes):
        print('%02x'%(ord(c)), end=' ')
        # xxx
        '''
        if ord(c) >= ord('a') and ord(c) <= ord('z'):
            sb.append(c)
        elif ord(c) >= ord('A') and ord(c) <= ord('Z'):
            sb.append(c)
        elif ord(c) >= ord('0') and ord(c) <= ord('0'):
            sb.append(c)
        '''
        if ord(c) >= ord(' ') and ord(c) <= ord('~'):
            sb.append(c)
        else:
            sb.append('.')
        if (idx+1) % 16 == 0:
            render_sb()
        elif (idx+1) % 8 == 0:
            sb.append(' | ')
            print('|', end=' ')
    idx += 1
    if (idx+1) % 16 != 0:
        while (idx+1) % 16 != 0:
            print('..', end=' ')
            sb.append(' ')
            if (idx+1) % 8 == 0:
                print('|', end=' ')
            idx += 1
        print('..', end=' ')
        render_sb()
    print('. (%s)'%(len(lst_bytes)))

