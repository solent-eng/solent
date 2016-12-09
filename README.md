# Project Overview

Event-driven networking library. Focused on providing tools for creating
sequencer-architecture systems. https://github.com/cratuki/solent/wiki

Parts of this system currently requires pygame. This is helpful for building
up terminal functionality while we are in development, but will be spun out
into a separate module at a later time. Solent-core will evolve into a
zero-dependency system.

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

We aim for this system to be multi-platform with no dependencies on other
libraries.

# Getting Started

Gather some ubuntu dependencies,

```bash
sudo apt-get install libportmidi-dev
```

Create a virtual env,

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
1) Network stuff

Have a look at the main function of solent.eng.scenarios, then try running one
like this:

    python3 -m solent.eng.scenarios

2) Nearcasting technique (aka aggressive use of the observer pattern)

Read through solent/gruel/server/spin_gruel_server.py. This is a simple app
that is built with nearcasting. You can launch an app that uses this as
follows:

    python3 -m solent.draft.gruel_server_sandbox

Telnet to the line console in another window:

    nc localhost 

Type some stuff (e.g. 'help')

The corresponding client demo (not quite working at time of writing):

    python3 -m solent.draft.gruel_client_sandbox

3) Terminal stuff

Some of this term stuff will be broken out into a separate package. But for
the moment it's here. Try:

    python3 -m solent.draft.turn_based_game --win

    python3 -m solent.draft.turn_based_game --tty

(Use qweadzxc to move the red thing around. This is less game than stripped
tech demo at the moment.)

```
(escape and then q to enter)

