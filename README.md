Codebase oriented around creating massively concurrent roguelike systems.

This will not be limited to games, but games will be possible.


= Solent client


== Some dependencies to get for ubuntu

````
sudo apt-get install libportmidi-dev
````


== Set up a virtual environment.

````
virtualenv -p python3 venv

# you'll need to do this for each development console you run
(cd venv; . bin/activate; cd ..)

pip install hg+http://bitbucket.org/pygame/pygame

# Haven't made this approach work so far
#pip install -r requirements.txt
````


== Install our code into it

````
pushd solent.client; pip install -e .; popd
````


== Things to try once it is installed

````
python3 -m solent.client.games.sandbox.py

python3 -m solent.client.games.sandbox.py --gui
````


== Packaging instructions

````
create a source client:
    python setup.py sdist

install to current virtualenv:
    pip install -e .
````

