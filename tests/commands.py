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

import unittest, replicant, re
import my_deployment

class TestCommands(unittest.TestCase):
    """Test case to test various commands"""

    def setUp(self):
        from replicant import Master, User, Final

        self.master = my_deployment.master
        self.masters = my_deployment.servers[0:1]
        self.slaves = my_deployment.servers[2:3]

        master_role = Master(User("repl_user", "xyzzy"))
        for master in self.masters:
            master_role.imbue(master)

        final_role = Final(self.masters[0])
        for slave in self.slaves:
            try:
                final_role.imbue(slave)
            except IOError:
                pass

    def testChangeMaster(self):
        "Test the change_master function"
        from replicant import change_master

        for slave in self.slaves:
            change_master(slave, self.master)

        self.master.sql("DROP TABLE IF EXISTS t1", db="test")
        self.master.sql("CREATE TABLE t1 (a INT)", db="test")
        self.master.disconnect()

        for slave in self.slaves:
            result = slave.sql("SHOW TABLES", db="test")

    def testSlaveWaitForPos(self):
        "Test the slave_wait_for_pos function"

        slave = self.slaves[0]
        master = self.master

        slave.sql("STOP SLAVE")
        pos1 = replicant.fetch_master_pos(master)
        replicant.change_master(slave, master, pos1)
        slave.sql("START SLAVE")

        master.sql("DROP TABLE IF EXISTS t1", db="test")
        master.sql("CREATE TABLE t1 (a INT)", db="test")
        master.sql("INSERT INTO t1 VALUES (1),(2)", db="test")
        pos2 = replicant.fetch_master_pos(master)
        replicant.slave_wait_for_pos(slave, pos2)
        pos3 = replicant.fetch_slave_pos(slave)
        self.assert_(pos3 >= pos2)

    def testSlaveWaitAndStop(self):
        "Test the slave_wait_and_stop function"

        slave = self.slaves[0]
        master = self.master

        slave.sql("STOP SLAVE")
        pos1 = replicant.fetch_master_pos(master)
        replicant.change_master(slave, master, pos1)
        slave.sql("START SLAVE")

        master.sql("DROP TABLE IF EXISTS t1", db="test")
        master.sql("CREATE TABLE t1 (a INT)", db="test")
        master.sql("INSERT INTO t1 VALUES (1),(2)", db="test")
        pos2 = replicant.fetch_master_pos(master)
        master.sql("INSERT INTO t1 VALUES (3),(4)", db="test")
        pos3 = replicant.fetch_master_pos(master)
        replicant.slave_wait_and_stop(slave, pos2)
        pos4 = replicant.fetch_slave_pos(slave)
        self.assertEqual(pos2, pos4)
        row = slave.sql("SELECT COUNT(*) AS count FROM t1", db="test")
        self.assertEqual(row['count'], 2)
        slave.sql("START SLAVE")
        replicant.slave_wait_and_stop(slave, pos3)
        row = slave.sql("SELECT COUNT(*) AS count FROM t1", db="test")
        self.assertEqual(row['count'], 4)

    def testSlaveStatusWaitUntil(self):
        "Test slave_status_wait_until"
        slave = self.slaves[0]
        master = self.master

        slave.sql("STOP SLAVE")
        pos1 = replicant.fetch_master_pos(master)
        replicant.change_master(slave, master, pos1)
        slave.sql("START SLAVE")
        

def suite():
    return unittest.makeSuite(TestCommands, 'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')


