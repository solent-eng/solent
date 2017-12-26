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

def solent_ext(ext, **args):
    python_path = 'solent.ext.%s.ext'%(ext)
    m = import_module(python_path)
    result = m.init_ext(**args)
    return result

def load_clib(ob):
    cl = ob.__class__
    #
    class_module = cl.__module__
    #
    api_filename = None
    system = platform.system()
    if system == 'Windows':
        api_filename = 'api.dll'
    else:
        api_filename = 'api.so'
    #
    wres_tokens = []
    wres_tokens.extend(class_module.split('.')[1:-1])
    wres_tokens.append(api_filename)
    path_so = dget_wres(*wres_tokens)
    #
    if not os.path.exists(path_so):
        raise Exception("Api file does not exist at {%s}"%(
            path_so))
    #
    clib = ctypes.cdll.LoadLibrary(path_so)
    log('clib')
    print(dir(clib))
    log('.')
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

