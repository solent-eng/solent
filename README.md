# Overview

Codebase oriented around creating massively concurrent roguelike systems.

The concurrency model will be a homage to the work of Josh Levine
(http://www.josh.com/notes/island-ecn-10th-birthday/). The project has been
developed from scratch on top of of gnu/linux and the python programming
language. The target platform is python3 on non-specific unix.

## Community

Except where specifically marked, the codebase will be licensed exclusively
under the GPL. I'd like to grow a community around this code that follows in
the spirit of _Social Architecture_ by Pieter Hintjens.

## Status

The code released in this repository is is not yet in a form where it will
feel accessible to anyone who checks it out.

There are several components sitting on my disk, and I'm in the process of
trying to bring each to a point where I can release it. These are the kinds of
components in play:

* Client code (terminal that can run in the tty or a window)

* Network engine (not yet upgraded to python3, see http://github.com/cratuki/eng.)

* Sequencer architecture built on the network engine

* Deployment coordination for the sequencer

I've started by releasing client code, with a loose plan to work backwards
through the stack from here. I figure I'll get the client code to a point
where someone who knew python could come along and use it to easily implement
a 7-day roguelike. This is not really a major focus of the project but it's an
achievable and well-fenced goal that forces me to get part of the codebase to
a public-release standard.

# Solent client notes

## Some dependencies to get for ubuntu

````
sudo apt-get install libportmidi-dev
````


## Set up a virtual environment.

````
virtualenv -p python3 venv

# you'll need to do this for each development console you run
(cd venv; . bin/activate; cd ..)

pip install hg+http://bitbucket.org/pygame/pygame

# Haven't made this approach work so far
#pip install -r requirements.txt
````


## Install our code into it

````
pushd solent.client; pip install -e .; popd
````


## Things to try once it is installed

````
python3 -m solent.client.games.sandbox.py

python3 -m solent.client.games.sandbox.py --gui
````


## Packaging instructions

````
create a source client:
    python setup.py sdist

install to current virtualenv:
    pip install -e .
````

