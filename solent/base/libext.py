# // license
# Copyright 2016, Free Software Foundation.
#
# This file is part of Solent.
#
# Solent is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# Solent is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# Solent. If not, see <http://www.gnu.org/licenses/>.

from .liblog import log

from solent import dget_wres

from importlib import import_module
import ctypes
import inspect
import os
import platform

SYSTEM = platform.system()

def solent_ext(ext, **args):
    """
    Python path should use dot notation to name the base path of the extension
    module directory. We will then load the 'ext' submodule of that path.

    Example.
    * You give python_path as 'solent.ext.windows_form_grid_console'.
    * This loads 'solent.ext.windows_form_grid_console.ext'.

    This steers people to create a single entrypoint for any modules they
    build: the 'ext' submodule.
    """
    ext_path = '%s.ext'%(ext)
    m = import_module(ext_path)
    result = m.init_ext(**args)
    return result

def load_clib(ob):
    cl = ob.__class__
    #
    class_module = cl.__module__
    #
    api_filename = None
    if SYSTEM == 'Windows':
        api_filename = 'api.dll'
    else:
        api_filename = 'api.so'
    #
    wres_tokens = []
    wres_tokens.extend(class_module.split('.')[1:-1])
    wres_tokens.append(api_filename)
    path_so = dget_wres(*wres_tokens)
    #
    print(f"Path to API sp: {path_so}")
    if not os.path.exists(path_so):
        raise Exception("Api file does not exist at {%s}"%(
            path_so))
    print("path_so: %s"%(path_so)) # xxx
    #
    # We are using cdll even in the Windows setting. Reason is comment here,
    # https://stackoverflow.com/questions/41760830/ctypes-procedure-probably-called-with-too-many-arguments-92-bytes-in-excess
    # Want to get advice from someone who groks C better than me on how to
    # standardise all this.
    clib = ctypes.cdll.LoadLibrary(path_so)
    return clib

def init_ext_fn(rtype, so_fn, alist):
    '''
    Useful for wrapping ctypes-loaded share library functions.
    
    Parameter order is modeled after C calling convention. Entries in rtpe and
    alist should be ctype types. Rtype can be None.

    C example,
        void        strlen(char*);

    Corresponding fields,
        rtype       so_fn(alist)
    '''
    fn = so_fn
    fn.argypes = alist
    fn.restype = rtype
    return fn

