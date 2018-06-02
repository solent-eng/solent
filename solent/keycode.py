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

# Ugh. This needs a refactor. I should rename it to ascii7bit. And then make
# all the fields exactly reflect convention. For example, get rid of the weird
# lmousedown situation.
#
# Perhaps I should rename 0x01 through to 0x1a as ctrl_a to ctrl_z. In
# practice, this is how we use them. But then comment the ascii arrangements.
class e_keycode(enum.Enum):
    # repurposing these values for mouse events
    nul           = 0x00
    lmousedown    = 0x01 # ctrl+a, in ascii this is start-of-heading
    lmouseup      = 0x02 # ctrl+b, in ascii this is end-of-heading
    etx           = 0x03 # ctrl+c
    eot           = 0x04 # ctrl+d
    rmousedown    = 0x05 # in ascii this is end-of-text
    rmouseup      = 0x06 # in ascii this is end-of-transmission
    xxx_0x07      = 0x07 # xxx
    #
    backspace     = 0x08
    tab           = 0x09
    newline       = 0x0a
    xxx_0x0b      = 0x0b
    xxx_0x0c      = 0x0c
    xxx_0x0d      = 0x0d
    xxx_0x0e      = 0x0e
    xxx_0x0f      = 0x0f
    dle           = 0x10 # ctrl+p
    dc1           = 0x11 # ctrl+q
    dc2           = 0x12 # ctrl+r
    dc3           = 0x13 # ctrl+s
    dc4           = 0x14 # ctrl+t
    nak           = 0x15 # ctrl+u
    xxx_0x16      = 0x16 # ctrl+v, rename
    xxx_0x17      = 0x17 # ctrl+v, rename
    xxx_0x18      = 0x18 # ctrl+x, rename
    xxx_0x19      = 0x19 # ctrl+y, rename
    xxx_0x1a      = 0x1a # ctrl+z, rename
    esc           = 0x1b # ctrl+[
    xxx_0x1c      = 0x1c # ctrl+|
    xxx_0x1d      = 0x1d # ctrl+]
    xxx_0x1e      = 0x1e
    space         = 0x20
    bang          = 0x21
    dquote        = 0x22
    hash          = 0x23
    dollar        = 0x24
    percent       = 0x25
    demon         = 0x26
    squote        = 0x27
    lparen        = 0x28
    rparen        = 0x29
    star          = 0x2a
    plus          = 0x2b
    comma         = 0x2c
    dash          = 0x2d
    period        = 0x2e
    slash         = 0x2f
    #
    n0            = 0x30
    n1            = 0x31
    n2            = 0x32
    n3            = 0x33
    n4            = 0x34
    n5            = 0x35
    n6            = 0x36
    n7            = 0x37
    n8            = 0x38
    n9            = 0x39
    qmark         = 0x3f
    rogue         = 0x40
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
    #
    rbracket      = 0x5b
    bslash        = 0x5c
    lbracket      = 0x5d
    hat           = 0x5e
    underscore    = 0x5f
    backtick      = 0x60
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
    lsquiggle     = 0x7b
    pipe          = 0x7c
    rsquiggle     = 0x7d
    tilde         = 0x7e
    xxx_0x7f      = 0x7f

def solent_keycode(name):
    '''
    Pass in the name of a member of e_keycode. This uses reflection to look it
    up from the enumeration itself, and returns the value of the selected
    item.
    '''
    l = dir(e_keycode)
    if name not in l:
        raise Exception("e_keycode.%s does not exist"%(name))
    return getattr(e_keycode, name).value

