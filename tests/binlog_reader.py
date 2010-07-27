# Copyright (c) 2010, Mats Kindahl, Charles Bell, and Lars Thalmann
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials
#       provided with the distribution.
#
#     * Neither the name of Sun Microsystems nor the names of its
#       contributors may be used to endorse or promote products
#       derived from this software without specific prior written
#       permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL SUN
# MICROSYSTEMS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

"""
Test of the binary log reader.
"""

import sys, os.path
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOTPATH = os.path.split(_HERE)[0]
sys.path.append(_ROOTPATH) 

import unittest
import glob

import replicant

class TestBinlogReader(unittest.TestCase):
    """
    Unit test for testing that the binlog reader works as
    expected. This test will read from a dump from mysqlbinlog to
    check that the parsing works as expected.
    """

    def test_size_and_pos(self):
        """
        Test that the length and end position of each event matches
        what is expected.
        """
        for fname in glob.iglob(os.path.join(_HERE, "data/mysqld-bin.*.txt")):
            istream = open(fname)
            current_pos = 4
            for event in replicant.binlog.read_events(istream):
                self.assertEqual(event.start_pos, current_pos)
                current_pos = event.end_pos

def suite():
    """
    Create a test suite for the binary log reader.
    """
    return unittest.makeSuite(TestBinlogReader, 'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

