#
# ip_validator
#
# // overview
# Simple mechanism for testing whether an IP is permissioned or not. At the
# time of writing there is no support for pattern matching. But it's easy
# to imagine now adding this without breaking the existing interface.
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

class IpValidator:
    def __init__(self):
        self.b_accept_any_ip = False
        self.permissioned_ips = []
    def clear(self):
        self.b_accept_any_ip = False
        self.permissioned_ips = []
    def accept_any_ip(self, b=True):
        self.b_accept_any_ip = b
    def is_ok(self, ip):
        if self.b_accept_any_ip:
            return True
        if ip in self.permissioned_ips:
            return True
        return False
    def add_ip(self, ip):
        if ip == '0.0.0.0':
            raise Exception("Please do not do this.")
        self.permissioned_ips.append(ip)

def ip_validator_new():
    ob = IpValidator()
    return ob

