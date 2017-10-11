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
# Engine gives a general-purpose facade around a select loop.
#
# It builds on solent.mem.
# 

import sys
if sys.version_info.major < 3:
    print("I'm only for python 3. (Have you activated your virtual env?)")
    sys.exit(1)

from .clock import Clock
from .engine import Engine
from .ip_validator import IpValidator
from .solent_quit_exception import SolentQuitException

