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
rootpath = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
sys.path.append(rootpath) 

import unittest, replicant

class TestBackup(unittest.TestCase):
    "Test case for various backup techniques"

    def setUp(self):
        
        self.backup = replicant.PhysicalBackup("file:/tmp/backup.tar.gz")
        
    def testPhysicalBackup(self):
        from my_deployment import master
        master.sql("CREATE TABLE IF NOT EXISTS dummy (a INT)", db="test")
        master.sql("INSERT INTO dummy VALUES (1),(2)", db="test")
        for row in master.sql("SELECT * FROM dummy", db="test"):
            self.assertTrue(row['a'] in [1, 2])
        self.backup.backup_server(master, ['test'])
        master.sql("DROP TABLE dummy", db="test")
        self.backup.restore_server(master)
        tbls = master.sql("SHOW TABLES", db="test")
        self.assertTrue('dummy' in [t["Tables_in_test"] for t in tbls])
        master.sql("DROP TABLE dummy", db="test")

def suite():
    return unittest.makeSuite(TestBackup)

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
