Codebase oriented around creating massively concurrent roguelike systems. This
project is still in its early days. What's here seeks to be accessible, but
there's not much here.

At the time of writing I'm focused on checking in client code. I've got a
sequencer architecture sitting here that I'll eventually be checking in. But
I'm building out from the client because I'd like the project to be community
accessible, not just a dump of my development directory.

Hence, this will not be limited to games.

But. It will be possible to build awesomely big games on it.

The concurrency model will be a homage to the work of Josh Levine
(http://www.josh.com/notes/island-ecn-10th-birthday/). The project has been
developed from scratch on top of of gnu/linux and the python programming
language. The target platform is python3 on non-specific unix.


# Solent client


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

