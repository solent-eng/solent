# Quickstart

```
git clone https://github.com/cratuki/solent.git

cd solent

virtualenv -p python3 venv
pushd venv; . bin/activate; popd
pip install pygame

# Run a demo of what we are building in solent.client.term
python -m solent.client.games.demo_experience --win

# Run a demo of the concurrency system we are building in solent.eng
python -m solent.demo.eng_sandbox
```

Things you can run

# Project Overview

The unifying idea behind solent is that we should define systems in terms of
messages.

The codebase is currently oriented towards creating massively concurrent
roguelike systems. That's a fun problema, and straightforward to iterate on.

This project has been developed from scratch.

## Concurrency

The target platform is python3
on non-specific unix. The concurrency model echoes the work of Josh Levine
(http://www.josh.com/notes/island-ecn-10th-birthday/).

## Interaction

Interaction is through a terminal-like user interface that is described in
solent/client.

The client follows a unifying idea, "everything is a sigil".

There's an issue to get this packaging an easy-to-download distribution
(https://github.com/cratuki/solent/issues/17). It is on major desktops and
unix tty, without external dependencies.

## Community

Except where specifically marked, the codebase will be licensed under the
LGPL, with copyright assigned to the FSF. I'd like to grow a community around
this code that follows in the spirit of _Social Architecture_ by Pieter
Hintjens.

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

# Getting Started

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

# directions

## solent.client

### generic client

It's intended that the client should be a generic interface to applications.
Client could connect to remote (server) applications. Or the apps could run in
the same process as client, but offering a consistent look and feel based off
sigils and thin-client interaction. (Think of it solent.client as being a bit
like a web browser, In a web browser, the building blocks are blocks of
free-flowing text and images. In solent.client, the building blocks are
character sigils, and a grid.)

### touch interface

Consider this: if the client could function as a touch interface or
keyboard-driven interface with no extra work required from the application
developer.

The challenge here is to flesh out a single touchable text widget, probably
something that required a modification to the definition of cgrid and keyboard
stream. (i.e. the cgrid would populate keyboard stream in response to
activity). With a single well-defined structure here, the rest becomes a
simple matter of implementation.

### oled-oriented layout system

Some high-end laptops now come with an OLED screen. In this screen, black
background is achieved by unpowered pixels.

See draft/000.layout.optimised.for.oled for a demonstration of a frame
layout system


