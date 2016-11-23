#!/bin/bash

pushd venv
. bin/activate
popd

#python -m solent.client.games.sandbox_a --tty
#python -m solent.client.games.sandbox_a --win
#python -m solent.client.games.demo_experience --tty
#python -m solent.client.games.demo_experience --win

#python -m solent.eng.scenarios

#python -m solent.draft.gruel_server_sandbox
python -m solent.draft.gruel_client_sandbox

