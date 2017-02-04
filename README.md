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


# Quickstart (unix systems)

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

# Install pygame (if you want - you can use curses instead), and see those
# same games now in a pygame window
pip3 install hg+https://bitbucket.org/pygame/pygame

python -m solent.release.snake --curses
python -m solent.release.snake --pygame

python -m solent.release.roguebox_00_weed_the_garden --curses
python -m solent.release.roguebox_00_weed_the_garden --pygame
```

If you want to understand the network layer, look at solent.eng.scenarios.


# Quickstart (Windows)

Install git for windows (from https://git-for-windows.github.io).

Install python 3.6 (other versions of python3 may work). On the launch screen,
select the option to add it to your PATH. Virtual env comes bundled in recent
releases of python.

Once you are in your git-for-windows shell, you can clone the repository,
create a virtual environment, and activate it. In these steps, be sure to use
the package virtualenv and not the reduced version of it that bundles with
recent versions of python (venv), as they behave differently. For example, you
don't get a unixy activate script with the venv module.

```bash
git clone https://github.com/cratuki/solent

cd solent

python -m virtualenv venv

. venv/bin/activate

pip install pygame

python -m solent.release.snake --pygame

python -m solent.release.roguebox_00_weed_the_garden --pygame
```

# Creating an installer/distribution

Here's how you create a distribution. This could be useful if you're trying to
create a release distro on another platform.

```bash
(Install python3.4 or later)

(Install SDL for your platform)

git clone github.com/cratuki/solent
cd solent

#
# // Create the virtual environment
python -m virtualenv venv

#
# // Activate the virtual environment
(cd venv; . bin/activate; cd ..)

#
# // If you didn't install a system-wide pygame, you can install it via pip.
pip3 install "hg+https://bitbucket.org/pygame/pygame"

#
# // Install other libraries we need in the virtualenv
pip3 install -r requirements.txt

#
# // Use pyinstaller to create the packages
#
# This works on unix, but won't work on Windows.
pyinstaller solent/pyinstaller/snake_curses.spec
#
# This should work anywhere that pygame is installed
pyinstaller solent/pyinstaller/snake_pygame.spec

#
# // Look in the dist directory for the resulting binaries
#
```

# What people are saying

"I definitely see the value, having gone through the pain of implementing
get/setsockopt. You've taken the common 5 or 6 steps required to get a BSD
socket up and running and boiled it down to a nice set of options. Kudos."
(Lead developer of a prominent free software project)

"I'm guessing you're off work, how long have you got for all this (really
jealous BTW). (,,,) So when I said jealous I meant of your time, you have
time, so jealous." (Former colleague)

"Apart from that you are apparently still not working? I am not exactly sure
what the problem is - do you need to go in a different direction?" (My mother)


