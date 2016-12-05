# Quickstart

```
git clone https://github.com/cratuki/solent.git

cd solent

virtualenv -p python3 venv
pushd venv; . bin/activate; popd
pip install pygame
# or: pip3 install hg+https://bitbucket.org/pygame/pygame

# Run a demo of what we are building in solent.client.term
python -m solent.client.games.demo_experience --win

# Run a demo of the concurrency system we are building in solent.eng
python -m solent.eng.scenarios
```

# Project Overview

Solent's central idea is we should define systems in terms of message
broadcasts. This model echoes the work of Josh Levine
(http://www.josh.com/notes/island-ecn-10th-birthday/).

You can see an example of a system defined in terms of messages in
solent.gruel.server. This is a network server which has been implemented using
the engine.

A good starting point is solent.eng.scenarios. This shows the engine being
applied to different purposes: tcp servers, tcp sockets, broadcast publishers
and listeners, and composites of these.

The solent.term package allows a developer to create a simple console that can
accept keystrokes and display a grid of characters. It targets major desktops
and unix tty, without external dependencies.


# Community/Contributions

Except where specifically marked, the codebase will be licensed under the
LGPL, with copyright assigned to the FSF. Contributions are welcome. See
[Contributing guidelines](CONTRIBUTING.md)


# Getting Started

Some dependencies to get for ubuntu:

````
sudo apt-get install libportmidi-dev
````

Set up a virtual environment.

````
virtualenv -p python3 venv

# you'll need to do this for each development console you run
(cd venv; . bin/activate; cd ..)

pip install hg+http://bitbucket.org/pygame/pygame

# Haven't made this approach work so far
#pip install -r requirements.txt
````

# Things to try

````
python3 -m solent.draft.turn_based_game --win

python3 -m solent.draft.turn_based_game --tty
````
(escape and then q to enter)


# future directions

## concurrency

Import more broadcast systems inspired by the Island model.

## web version of term

It's intended that the client should be a generic interface to applications.
Client could connect to remote (server) applications. Or the apps could run in
the same process as client, but offering a consistent look and feel based off
sigils and thin-client interaction. (Think of it solent.client as being a bit
like a web browser, In a web browser, the building blocks are blocks of
free-flowing text and images. In solent.client, the building blocks are
character sigils, and a grid.)

## touch interface version of term

Consider this: if the client could function as a touch interface or
keyboard-driven interface with no extra work required from the application
developer.

The challenge here is to flesh out a single touchable text widget, probably
something that required a modification to the definition of cgrid and keyboard
stream. (i.e. the cgrid would populate keyboard stream in response to
activity). With a single well-defined structure here, the rest becomes a
simple matter of implementation.

## oled-oriented layout

Some high-end laptops now come with an OLED screen. In this screen, black
background is achieved by unpowered pixels.

Run python -m solent.draft.oled_ui_demo to see a mock frame layout system.


