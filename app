#!/usr/bin/env bash

BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="$BASE_DIR/venv"


# --------------------------------------------------------
#   activate the virtual environment
# --------------------------------------------------------
if [[ ! -e $VENV_DIR ]]; then
    echo "ERROR: First up a virtual env directory at $VENV_DIR"
    exit 1
fi

pushd $VENV_DIR
. bin/activate
popd


# --------------------------------------------------------
#   launchers
# --------------------------------------------------------
#
# Test launchers
python -m run_tests
#python -m testing.util.rail_bytesetter

#
# Release
#python -m solent.demo.snake
#python -m solent.demo.weeds

#
# Scenarios
#python -m solent.scenarios.eng_10_orb_nearcast_and_cog_basics
#python -m solent.scenarios.eng_20_orb_hosted_tcp_server
#python -m solent.scenarios.eng_21_line_console
#python -m solent.scenarios.eng_40_simple_udp_sub
#python -m solent.scenarios.eng_41_simple_udp_pub
#python -m solent.scenarios.eng_90_command_console

#
# Tools
#python -m solent.tools.qd_listen 127.255.255.255 50000
#python -m solent.tools.qd_poll 127.255.255.255 50000
#python -m solent.tools.tclient localhost 5001

#
# Wrapping C
#python -m wsrc.build_all
#python -m solent.draft.wrap_c_code

#
# Console
#python -m solent.draft.console_demo --curses
#python -m solent.draft.console_demo --pygame

#
# Drafting
#python -m solent.draft.demonstrate_line_console
#python -m solent.draft.draw
#python -m solent.draft.gollop_box
#python -m solent.draft.gruel_server_sandbox
#python -m solent.draft.gruel_client_sandbox --pygame
#python -m solent.draft.mountain_box --pygame
#python -m solent.draft.oled_ui_demo
#python -m solent.draft.redis_client
#python -m solent.draft.roguebox --pygame
#python -m solent.draft.sdl
#python -m solent.draft.turn_based_game --curses
#python -m solent.draft.turn_based_game --pygame

#
# Other
#python -m solent.eng.profile_event_loop

