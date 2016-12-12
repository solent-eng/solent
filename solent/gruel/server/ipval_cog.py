#
# ipval_cog
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

from solent.eng import ip_validator_new
from solent.log import log

class IpvalCog(object):
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.ip_validator = ip_validator_new()
    #
    def on_ipval_add_ip(self, ip):
        self.ip_validator.add_ip(
            ip=ip)
    def on_ipval_disable(self):
        self.ip_validator.accept_any_ip()
    def on_announce_tcp_connect(self, ip, port):
        if self.ip_validator.is_ok(ip):
            self.orb.nearcast(
                cog=self,
                message_h='nearnote',
                s='confirm that %s is ok'%(ip))
        else:
            log('invalid ip %s'%ip)
            self.orb.nearcast(
                cog=self,
                message_h='please_tcp_boot')

def ipval_cog_new(cog_h, orb, engine):
    ob = IpvalCog(
        cog_h=cog_h,
        orb=orb,
        engine=engine)
    return ob

