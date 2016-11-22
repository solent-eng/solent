#
# kv_source
#
# // overview
# This is a way for creating shared variables that you can access from any
# part of the codebase without them being global. You can either declare a
# namespace in your code, or you can load from a delimited file of a
# particular structure so that it can be used as a var source.
#
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

def read_file(fname):
    f_ptr = open(fname)
    data = f_ptr.read()
    f_ptr.close()
    return data

STORES = {}
def create_kv_source_singleton(source_name, d):
    global STORES
    if source_name in STORES:
        raise Exception("multiple init calls [%s]"%(source_name))
    STORES[source_name] = d

def kv_source_get(source_name, key):
    global STORES
    return STORES[source_name][key]

def kv_source_clear(source_name):
    global STORES
    del STORES[source_name]

def kv_source_exists(source_name):
    global STORES
    if source_name in STORES:
        return True
    return False

def kv_source_load_dict_from_file(source_name, path_to_kv_file):
    data = read_file(path_to_kv_file)
    lines = data.split('\n')
    rows = [l.split('|') for l in lines
        if len(l.strip()) > 0
        and not l.strip().startswith('#')]
    #
    # quick validation
    assert len(rows[0]) == 3
    assert rows[0][0] == 'c'
    assert rows[0][1] == 'key'
    assert rows[0][2] == 'value'
    for r in rows[1:]:
        assert len(r) == 3
        assert r[0] == 'd'
    #
    # let's extract it
    d = {}
    for r in rows[1:]:
        d[r[1].strip()] = r[2].strip()
    create_kv_source_singleton(source_name, d)

def kv_source_register_dict(source_name, d):
    create_kv_source_singleton(source_name, d)

