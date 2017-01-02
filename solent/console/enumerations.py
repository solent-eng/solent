#
# enumerations
#
# // overview
# constants for the term package
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

import enum

class e_colpair(enum.Enum):
    "colour pairs"
    red_t         = 1000
    green_t       = 1001
    yellow_t      = 1002
    blue_t        = 1003
    purple_t      = 1004
    cyan_t        = 1005
    white_t       = 1006
    t_red         = 1007
    t_green       = 1008
    t_yellow      = 1009
    white_blue    = 1010
    white_purple  = 1011
    black_cyan    = 1012
    t_white       = 1013

class e_boxtype(enum.Enum):
    line          = 2000
    edge          = 2001
    void          = 2002
    hash          = 2003
    stop          = 2004

class e_keycode(enum.Enum):
    # repurposing these values for mouse events
    none          = 0x0
    lmousedown    = 0x1  # in ascii this is start-of-heading
    lmouseup      = 0x2  # in ascii this is end-of-heading
    rmousedown    = 0x3  # in ascii this is end-of-text
    rmouseup      = 0x4  # in ascii this is end-of-transmission
    #
    backspace     = 0x8
    tab           = 0x9
    newline       = 0xa
    esc           = 0x1b
    #
    a             = 0x61
    b             = 0x62
    c             = 0x63
    d             = 0x64
    e             = 0x65
    f             = 0x66
    g             = 0x67
    h             = 0x68
    i             = 0x69
    j             = 0x6a
    k             = 0x6b
    l             = 0x6c
    m             = 0x6d
    n             = 0x6e
    o             = 0x6f
    p             = 0x70
    q             = 0x71
    r             = 0x72
    s             = 0x73
    t             = 0x74
    u             = 0x75
    v             = 0x76
    w             = 0x77
    x             = 0x78
    y             = 0x79
    z             = 0x7a
    #
    A             = 0x41
    B             = 0x42
    C             = 0x43
    D             = 0x44
    E             = 0x45
    F             = 0x46
    G             = 0x47
    H             = 0x48
    I             = 0x49
    J             = 0x4a
    K             = 0x4b
    L             = 0x4c
    M             = 0x4d
    N             = 0x4e
    O             = 0x4f
    P             = 0x50
    Q             = 0x51
    R             = 0x52
    S             = 0x53
    T             = 0x54
    U             = 0x55
    V             = 0x56
    W             = 0x57
    X             = 0x58
    Y             = 0x59
    Z             = 0x5a

def key(name):
    '''
    Convenience function. This saves us having to type e_keycode.blah.value.
    The 'dot value' bit is a hassle, and I keep forgetting to do it.
    '''
    l = dir(e_keycode)
    if name not in l:
        raise Exception("e_keycode.%s does not exist"%(name))
    return getattr(e_keycode, name).value

