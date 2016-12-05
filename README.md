# Project Overview

Event-driven networking library. Focused on providing tools for creating
sequencer-architecture systems. https://github.com/cratuki/solent/wiki

# Quickstart

```bash
git clone https://github.com/cratuki/solent.git

cd solent

virtualenv -p python3 venv
pushd venv; . bin/activate; popd

# Demo of the solent.eng concurrency system
python -m solent.eng.scenarios

# Run a demo of what we are building in solent.term (requires pygame)
pip3 install hg+https://bitbucket.org/pygame/pygame
python -m solent.draft.turn_based_game --win

# TTY version of the console
python -m solent.draft.turn_based_game --tty
```

# Community/Contributions

Except where specifically marked, the codebase will be licensed under the
LGPL, with copyright assigned to the FSF. Contributions are welcome. See
[Contributing guidelines](CONTRIBUTING.md)

# Getting Started

Gather some ubuntu dependencies,

```bash
sudo apt-get install libportmidi-dev
```

Set up a virtual environment,

```bash
virtualenv -p python3 venv

# you'll need to do this for each development console you run
(cd venv; . bin/activate; cd ..)

pip install hg+http://bitbucket.org/pygame/pygame

# Haven't made this approach work so far
#pip install -r requirements.txt
```

Things to try,

```bash
python3 -m solent.draft.turn_based_game --win

python3 -m solent.draft.turn_based_game --tty
```
(escape and then q to enter)

