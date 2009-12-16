# Copyright (c) 2009, Sun Microsystems, Inc.
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
here = os.path.dirname(os.path.abspath(__file__))
rootpath = os.path.split(here)[0]
sys.path.append(rootpath) 

import unittest, mysqlrep, re
import my_deployment

class TestRoles(unittest.TestCase):
    """Test case to test role usage."""

    def setUp(self):
        self.master = my_deployment.master
        self.slave = my_deployment.slaves[0]
        self.slaves = my_deployment.slaves

    def _imbueRole(self, role):
        # We are likely to get an IOError because we cannot write the
        # configuration file, but this is OK.
        try:
            role.imbue(self.master)
        except IOError:
            pass

    def testMasterRole(self):
        "Test how the master role works"
        self._imbueRole(mysqlrep.Master(mysqlrep.User("repl_user", "xyzzy")))
        
    def testSlaveRole(self):
        "Test that the slave role works"
        self._imbueRole(mysqlrep.Final(self.master))

    def testRelayRole(self):
        "Test that the slave role works"
        self._imbueRole(mysqlrep.Relay(self.master))

def suite():
    return unittest.makeSuite(TestRoles, 'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
