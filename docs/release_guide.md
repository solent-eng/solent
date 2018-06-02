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

