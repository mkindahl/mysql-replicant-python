import sys, os.path
here = os.path.dirname(os.path.abspath(__file__))
rootpath = os.path.split(here)[0]
sys.path.append(rootpath) 

import unittest, mysqlrep, re
import my_deployment

_POSITION_CRE = re.compile(r"Position\(\d+, '\w+-bin.\d+', \d+\)")

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
        self.assertTrue(_POSITION_CRE.match(str(position)))
        self.master.disconnect()

    def testGetSlavePosition(self):
        "Fetching slave positions from the slaves and checking format"
        for slave in self.slaves:
            slave.connect()
            position = mysqlrep.fetch_slave_pos(slave)
            self.assertTrue(_POSITION_CRE.match(str(position)))
            slave.disconnect()

def suite():
    return unittest.makeSuite(TestServerBasics, 'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

