#!/bin/bash

pushd venv
. bin/activate
popd

#
# Networking
#
#python -m solent.eng.scenarios

#
# Release
#
python -m solent.release.snake --pygame
#python -m solent.release.roguebox_00_weed_the_garden --pygame

#
# Tools
#
#python -m solent.tools.qd_listen 127.255.255.255 50000
#python -m solent.tools.qd_poll 127.255.255.255 50000
#python -m solent.tools.tclient localhost 5001

#
# Wrapping C
#
#python -m wsrc.build_all
#python -m solent.draft.wrap_c_code

#
# Console
#
#python -m solent.draft.console_demo --curses
#python -m solent.draft.console_demo --pygame

#
# Other drafting
#
#python -m solent.draft.demonstrate_line_console
#python -m solent.draft.draw
#python -m solent.draft.gollop_box
#python -m solent.draft.gruel_server_sandbox
#python -m solent.draft.gruel_client_sandbox --pygame
#python -m solent.draft.mountain_box --pygame
#python -m solent.draft.oled_ui_demo
#python -m solent.draft.roguebox --pygame
#python -m solent.draft.sdl
#python -m solent.draft.turn_based_game --curses
#python -m solent.draft.turn_based_game --pygame

