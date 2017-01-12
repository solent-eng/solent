# Project Overview

Sequencer-architecture platform. Currently most of it is written in python.

Elements:

* eng.engine: Concurrency engine. Uses async networking patterns (e.g. select)

* gruel: simple bidirection async protocol for transmitting arbitrary payloads

* term: textual user interface

* nearcasting: An in-process mechanism for broadcasting messages

* mechanisms to build shared libraries and access them from python


# Community/Contributions

Except where specifically marked, the codebase will be licensed under the
LGPL, with copyright assigned to the FSF. Contributions are welcome. See
[Contributing guidelines](CONTRIBUTING.md)

We aim for this system to be multi-platform with no dependencies on other
libraries.


# Quickstart

This will get you seeing some basic stuff

```bash
git clone https://github.com/cratuki/solent.git

cd solent

bin/arrange_dependencies

# Whenever you open a new prompt, do this to make your
# virtual env active
(cd venv; . bin/activate; cd ..)

# Demo of the solent.eng concurrency system
python -m solent.eng.scenarios

# Demo of the snake game (skip this on windows)
python -m solent.draft.snake --curses

# Demo of a turn-based game (skip this on windows)
python -m solent.draft.turn_based_game --curses

# Install pygame, and see those same games now in a pygame window
pip3 install hg+https://bitbucket.org/pygame/pygame
python -m solent.draft.turn_based_game --snake
python -m solent.draft.turn_based_game --pygame
```

Things to try,

```bash
(cd venv; . bin/activate; cd ..)

// Network stuff

Have a look at the main function of solent.eng.scenarios, then try running one
like this:

    python3 -m solent.eng.scenarios

// Games as tech-demos

    python3 -m solent.draft.snake --pygame

(Use awdx, and tab to switch out to menu)

    python3 -m solent.draft.turn_based_game --pygame

(Use qweadzxc to move the @ around. There is not much here at the moment)

```

Here's how you create a distribution. This could be useful if you're trying to
create a release distro on another platform.

```bash
Install python3.4 or later

Install hg (we need it for pygame - ick)

git clone github.com/cratuki/solent

cd solent
virtualenv -p python3

#
# activate the virtual environment
#
# on unix:
    (cd venv; . bin/activate; cd ..)
# on windows:
    cd venv
    bin\activate.bat
    cd ..

pip3 install "hg+https://bitbucket.org/pygame/pygame"

pip3 install -r requirements.txt

#
# On unix or mac os. This won't work on Windows
pyinstaller solent/pyinstaller/snake_curses.spec
#
# This should work everywhere so long as pygame installed above.
pyinstaller solent/pyinstaller/snake_pygame.spec

#
# The resulting binaries are in the dist directory
#
```


