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
#
# // overview
# Bona File is a very simple file transfer mechanism that runs over TCP. It
# fills a similar role to TFTP in that it is trivial to implement, and
# feature-poor. But, in contrast to TFP it is authenticated, and it runs over
# TCP.
#
# // protocol
# See equivalent section in rail_bona_file_server.

import struct

class CsBonaFileError:
    def __init__(self):
        self.bona_file_h = None
        self.msg = None

class CsBonaFileBlock:
    def __init__(self):
        self.bona_file_h = None
        self.bb = None

class CsBonaFileFinis:
    def __init__(self):
        self.bona_file_h = None

class RailBonaFileClient:
    def __init__(self):
        self.cs_bona_file_error = CsBonaFileError()
        self.cs_bona_file_block = CsBonaFileBlock()
        self.cs_bona_file_finis = CsBonaFileFinis()
    def zero(self, cb_bona_file_error, cb_bona_file_block, cb_bona_file_finis):
        self.cb_bona_file_error = cb_bona_file_error
        self.cb_bona_file_block = cb_bona_file_block
        self.cb_bona_file_finis = cb_bona_file_finis
        #
    #
    def seek(self, bona_file_h, addr, port, relpath):
        xxx



