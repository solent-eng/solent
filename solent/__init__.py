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

# Below: order matters!

from .paths import are_we_in_a_pyinstaller_bundle
from .paths import dget_root
from .paths import dget_static
from .paths import dget_wres

# small
from .base import uniq
from .base import ns
# log
from .base import hexdump_bytes
from .base import hexdump_string
from .base import log
from .base import init_logging
# test
from .base import clear_tests
from .base import have_tests
from .base import run_tests
from .base import test
# mempool
from .base import Mempool
# ref
from .base import ref_create
from .base import ref_lookup
from .base import ref_acquire
from .base import ref_release
# rail_line_finder
from .base import RailLineFinder
# interface script
from .base import parse_line_to_tokens
from .base import init_interface_script_parser
from .base import SignalConsumer

from .eng import Clock
from .eng import Engine
from .eng import SolentQuitException

# Above this point, solent is structured into a clear dependency hierarchy.
# After this point, it becomes less-deliberate, shabby. At the time of
# writing, we could further improve things by putting all console-style
# functionality into a console or term module, and then arranging that
# below this point.

from .cpair import solent_cpair
from .cpair import solent_cpair_pairs
from .keycode import solent_keycode

