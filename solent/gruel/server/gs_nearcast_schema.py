#
# gs_nearcast_schema
#
# // overview
# Gruel server's nearcast schema.
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

from solent.eng import nearcast_schema_new
from solent.log import log

I_NEARCAST_GRUEL_SERVER = '''
    i message h
        i field h

    message nearnote
        field s

    message ipval_add_ip
        field ip

    message ipval_disable

    message start_service
        field ip
        field port
        field password

    message stop_service

    message announce_tcp_connect
        field ip
        field port

    message announce_tcp_condrop

    message please_tcp_boot

    # A message from the client that has not yet been through the login cog.
    # Once a TCP connection is done, all activity should flow to the login
    # authority, which can unpack it into useful messages.
    message gruel_recv
        field d_gruel

    message gruel_send
        field payload

    message announce_login
        field max_packet_size
        field max_fulldoc_size

    # received from the client
    message doc_recv
        field doc

    # to send to the client
    message doc_send
        field doc

    message heartbeat_recv

    message heartbeat_send

'''

def gs_nearcast_schema_new():
    ob = nearcast_schema_new(
        i_nearcast=I_NEARCAST_GRUEL_SERVER)
    return ob

