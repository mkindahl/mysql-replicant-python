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

_POS_CRE = re.compile(r"Position\((\d+, '\w+-bin.\d+', \d+)?\)")

class TestServerBasics(unittest.TestCase):
    """Test case to test server basics. It relies on an existing MySQL
    server"""

    def setUp(self):
        self.master = my_deployment.master
        self.slave = my_deployment.slaves[0]
        self.slaves = my_deployment.slaves
        
    def testConfig(self):
        "Get some configuration information from the server"
        self.assertEqual(self.master.host, "localhost")
        self.assertEqual(self.master.port, 3307)
        self.assertEqual(self.master.socket, '/var/run/mysqld/mysqld1.sock')

    def testFetchReplace(self):
        "Fetching a configuration file, adding some options, and replacing it"
        self.master.fetch_config(os.path.join(here, 'test.cnf'))
        self.assertEqual(self.master.get_option('user'), 'mysql')
        self.assertEqual(self.master.get_option('log-bin'),
                         '/var/log/mysql/master-bin')
        self.assertEqual(self.master.get_option('slave-skip-start'), None)
        self.master.set_option('no-value')
        self.assertEqual(self.master.get_option('no-value'), None)
        self.master.set_option('with-int-value', 4711)
        self.assertEqual(self.master.get_option('with-int-value'), '4711')
        self.master.set_option('with-string-value',
                               'Careful with that axe, Eugene!')
        self.assertEqual(self.master.get_option('with-string-value'),
                         'Careful with that axe, Eugene!')
        self.master.replace_config(os.path.join(here, 'test-new.cnf'))
        lines1 = file(os.path.join(here, 'test.cnf')).readlines()
        lines2 = file(os.path.join(here, 'test-new.cnf')).readlines()
        lines1 += ["\n", "no-value\n", "with-int-value = 4711\n",
                   "with-string-value = Careful with that axe, Eugene!\n"]
        lines1.sort()
        lines2.sort()
        self.assertEqual(lines1, lines2)
        os.remove(os.path.join(here, 'test-new.cnf'))

        
    def testSsh(self):
        "Testing ssh() call"
        self.assertEqual(''.join(self.master.ssh(["echo", "-n", "Hello"])),
                         "Hello")
 
    def testSql(self):
        "Testing (read-only) SQL execution"
        self.master.connect()
        self.assertEqual(self.master.sql("select 'Hello' as val")['val'],
                         "Hello")
        self.master.disconnect()

    def testLockUnlock(self):
        "Test that the lock and unlock functions can be called"
        self.master.connect()
        mysqlrep.flush_and_lock_database(self.master)
        mysqlrep.unlock_database(self.master)
        self.master.disconnect()

    def testGetMasterPosition(self):
        "Fetching master position from the master and checking format"
        self.master.connect()
        position = mysqlrep.fetch_master_pos(self.master)
        self.assertTrue(position is None or _POS_CRE.match(str(position)),
                        "Position '%s' is not correct" % (str(position)))
        self.master.disconnect()

    def testGetSlavePosition(self):
        "Fetching slave positions from the slaves and checking format"
        for slave in self.slaves:
            try:
                slave.connect()
                position = mysqlrep.fetch_slave_pos(slave)
                self.assertTrue(_POS_CRE.match(str(position)),
                                "Incorrect position '%s'" % (str(position)))
                slave.disconnect()
            except mysqlrep.EmptyRowError:
                pass

def suite():
    return unittest.makeSuite(TestServerBasics, 'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

