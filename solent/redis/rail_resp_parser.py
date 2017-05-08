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

class CsRespHead:
    def __init__(self):
        pass

class CsRespTail:
    def __init__(self):
        pass

class CsRespStr:
    def __init__(self):
        pass

class CsRespErr:
    def __init__(self):
        pass

class CsRespInt:
    def __init__(self):
        pass

class CsRespArrInc:
    def __init__(self):
        pass

class CsRespArrDec:
    def __init__(self):
        pass

class RailRespAssembler:
    def __init__(self, cb_resp_head, cb_resp_tail, cb_resp_str, cb_resp_err, cb_resp_int, cb_resp_arr_inc, cb_resp_arr_dec):
        self.cb_resp_head = cb_resp_head
        self.cb_resp_tail = cb_resp_tail
        self.cb_resp_str = cb_resp_str
        self.cb_resp_err = cb_resp_err
        self.cb_resp_int = cb_resp_int
        self.cb_resp_arr_inc = cb_resp_arr_inc
        self.cb_resp_arr_dec = cb_resp_arr_dec
        #
        self.cs_resp_head = CsRespHead()
        self.cs_resp_tail = CsRespTail()
        self.cs_resp_str = CsRespStr()
        self.cs_resp_err = CsRespErr()
        self.cs_resp_int = CsRespInt()
        self.cs_resp_arr_inc = CsRespArrInc()
        self.cs_resp_arr_dec = CsRespArrDec()

def rail_resp_assembler_new(cb_resp_head, cb_resp_tail, cb_resp_str, cb_resp_err, cb_resp_int, cb_resp_arr_inc, cb_resp_arr_dec):
    ob = RailRespAssembler(
        cb_resp_head=cb_resp_head,
        cb_resp_tail=cb_resp_tail,
        cb_resp_str=cb_resp_str,
        cb_resp_err=cb_resp_err,
        cb_resp_int=cb_resp_int,
        cb_resp_arr_inc=cb_resp_arr_inc,
        cb_resp_arr_dec=cb_resp_arr_dec)
    return ob

class CsParseData:
    def __init__(self):
        self.parse_h = None
        self.tree = None

STATE_IDLE = 'idle'
STATE_OPEN = 'open'

class RailRespParser:
    def __init__(self, cb_parse_data):
        self.cb_parse_data = cb_parse_data
        #
        self.cs_parse_data = CsParseData()
        #
        self.state = STATE_IDLE
        self.parse_h = None
        #
        self.rail_resp_assembler = RailRespAssembler(
            cb_resp_head=self.cb_resp_head,
            cb_resp_tail=self.cb_resp_tail,
            cb_resp_str=self.cb_resp_str,
            cb_resp_err=self.cb_resp_err,
            cb_resp_int=self.cb_resp_int,
            cb_resp_arr_inc=self.cb_resp_arr_inc,
            cb_resp_arr_dec=self.cb_resp_arr_dec)
    def open(self, parse_h):
        if self.state == STATE_OPEN:
            raise Exception("already open")
        #
        self.parse_h = parse_h
        self.state = STATE_OPEN
    def close(self):
        if self.state != STATE_OPEN:
            raise Exception("not open")
        #
        self.parse_h = None
        self.state = STATE_IDLE
    def accept(self, s):
        raise Exception('not yet implemented')

def rail_resp_parser_new(cb_parse_data):
    ob = RailRespParser(
        cb_parse_data=cb_parse_data)
    return ob

