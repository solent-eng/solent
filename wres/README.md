Directory tree for dynamically linked libraries to be wrapped by solent.
Structure should map closely to the package structure of tree solent.

# Structure of this res area

The centre of solent's package system is the python source tree under /solent.
Here I will explain this package's structure is subservient to that.

Raw source code is stored in /src. This gets compiled into targets in this
area.

The directory that these artifacts are targetted should match the code that
the python tree uses. For example, if there is a class at
solent.audio.wrapper, then that class will be in /solent/audio/wrapper.py.
Following from this, the res directory should be /res/audio/wrapper/api.so
Any other code resources can live under that directory as well. For the
moment, don't worry about duplication. Just exactly match the python
structure.

