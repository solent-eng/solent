#
# ip_validator (testing)
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

from testing import run_tests
from testing import test
from testing.util import clock_fake

from solent.eng import ip_validator_new

import sys

@test
def should_accept_and_reject_ips():
    test_ip = '127.0.0.1'
    second_ip = '203.15.93.2'
    #
    ip_validator = ip_validator_new()
    ip_validator.add_ip(
        ip=test_ip)
    #
    assert True == ip_validator.is_ok(
        ip=test_ip)
    assert False == ip_validator.is_ok(
        ip=second_ip)
    #
    ip_validator.add_ip(
        ip=second_ip)
    assert True == ip_validator.is_ok(
        ip=test_ip)
    assert True == ip_validator.is_ok(
        ip=second_ip)
    #
    return True

@test
def should_allow_all_ips_to_be_accepted():
    test_ip = '127.0.0.1'
    second_ip = '203.15.93.2'
    #
    ip_validator = ip_validator_new()
    #
    assert False == ip_validator.is_ok(
        ip=test_ip)
    #
    ip_validator.accept_any_ip()
    #
    assert True == ip_validator.is_ok(
        ip=test_ip)
    #
    return True

@test
def should_clear_when_told_to():
    first_ip = '127.0.0.1'
    second_ip = '203.15.93.2'
    #
    ip_validator = ip_validator_new()
    assert False == ip_validator.is_ok(
        ip=first_ip)
    assert False == ip_validator.is_ok(
        ip=second_ip)
    #
    ip_validator.add_ip(
        ip=first_ip)
    assert True == ip_validator.is_ok(
        ip=first_ip)
    assert False == ip_validator.is_ok(
        ip=second_ip)
    #
    ip_validator.accept_any_ip()
    assert True == ip_validator.is_ok(
        ip=first_ip)
    assert True == ip_validator.is_ok(
        ip=second_ip)
    #
    ip_validator.clear()
    assert False == ip_validator.is_ok(
        ip=first_ip)
    assert False == ip_validator.is_ok(
        ip=second_ip)
    #
    return True

if __name__ == '__main__':
    run_tests(
        unders_file=sys.modules['__main__'].__file__)

