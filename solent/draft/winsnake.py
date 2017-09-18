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

from solent.demo.snake import launch

from solent import Engine
from solent import SolentQuitException

MTU = 1490

def main():
    print("This is stub code to allow us to create a native-Windows console")
    print("At the time of writing, that console is unfinished.")
    print("(Hence, this will crash shortly.)")
    #
    console_type = 'windows'
    #
    engine = Engine(
        mtu=MTU)
    try:
        engine.default_timeout = 0.01
        launch(
            engine=engine,
            console_type=console_type)
    except SolentQuitException:
        pass
    finally:
        engine.close()

if __name__ == '__main__':
    main()

