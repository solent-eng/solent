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
#python -B -m run_tests

#
# Release
#python -B -m solent.demo.draw
python -B -m solent.demo.snake
#python -B -m solent.demo.weeds

#
# Scenarios
#python -B -m solent.scenarios.eng_10_orb_nearcast_and_cog_basics
#python -B -m solent.scenarios.eng_20_orb_hosted_tcp_server
#python -B -m solent.scenarios.eng_21_line_console
#python -B -m solent.scenarios.eng_40_simple_udp_sub
#python -B -m solent.scenarios.eng_41_simple_udp_pub
#python -B -m solent.scenarios.eng_90_command_console

#
# Tools
#python -B -m solent.tools.qd_listen 127.255.255.255 50000
#python -B -m solent.tools.qd_poll 127.255.255.255 50000
#python -B -m solent.tools.tclient localhost 5001 # nc -l -p 5001

#
# Wrapping C
#python -B -m wsrc.build_all
#python -B -m solent.draft.wrap_c_code

#
# Console
#python -B -m solent.draft.console_demo --curses
#python -B -m solent.draft.console_demo --pygame

#
# Drafting
#python -B -m solent.draft.demonstrate_line_console
#python -B -m solent.draft.gollop_box
#python -B -m solent.draft.mountain_box --pygame
#python -B -m solent.draft.oled_ui_demo
#python -B -m solent.draft.redis_client
#python -B -m solent.draft.sdl
#python -B -m solent.draft.turn_based_game --curses
#python -B -m solent.draft.turn_based_game --pygame
#python -B -m solent.draft.winsnake

#
# Other
#python -B -m solent.eng.profile_event_loop

