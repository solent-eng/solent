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

from .impl_grid_console import ImplGridConsole

from solent import log

def init_ext(zero_h, cb_grid_console_splat, cb_grid_console_kevent, cb_grid_console_mevent, cb_grid_console_closed, engine, width, height):
    impl_grid_console = ImplGridConsole()
    impl_grid_console.zero(
        zero_h=zero_h,
        cb_grid_console_splat=cb_grid_console_splat,
        cb_grid_console_kevent=cb_grid_console_kevent,
        cb_grid_console_mevent=cb_grid_console_mevent,
        cb_grid_console_closed=cb_grid_console_closed,
        engine=engine,
        width=width,
        height=height)
    #
    form_grid_console = impl_grid_console.form
    return form_grid_console

