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

import sys, os.path
rootpath = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
sys.path.append(rootpath) 

import unittest
import replicant

class TestPosition(unittest.TestCase):
    "Test case for binlog positions class."
    def _checkPos(self, p, s):
        """Check that a position is valid, have the expected
        representation, and can be converted from string
        representation to class and back."""
        from replicant import Position
        self.assertEqual(repr(p), s)
        self.assertEqual(p, eval(repr(p)))
        self.assertEqual(s, repr(eval(s)))
        
    def testSimple(self):
        from replicant import Position
        positions = [Position('master-bin.00001', 4711),
                     Position('master-bin.00001', 9393),
                     Position('master-bin.00002', 102)]
        strings = ["Position('master-bin.00001', 4711)",
                   "Position('master-bin.00001', 9393)",
                   "Position('master-bin.00002', 102)"]
 
        for i in range(0,len(positions)-1):
            self._checkPos(positions[i], strings[i])

        # Check that comparison works as expected.
        for i in range(0, len(positions)-1):
            for j in range(0, len(positions)-1):
                if i < j:
                    self.assertTrue(positions[i] < positions[j])
                elif i == j:
                    self.assertEqual(positions[i], positions[j])
                else:
                    self.assertTrue(positions[i] > positions[j])

def suite():
    return unittest.makeSuite(TestPosition)

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
