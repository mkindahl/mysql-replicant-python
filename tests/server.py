import sys, os.path
here = os.path.dirname(os.path.abspath(__file__))
rootpath = os.path.split(here)[0]
sys.path.append(rootpath) 

import unittest
import mysqlrep

class TestServerBasics(unittest.TestCase):
    """Test case to test server basics. It relies on an existing MySQL
    server"""
    def setUp(self):
        from mysqlrep import Server, User, Linux
        self.server = Server(sql_user=User("mats"),
                             ssh_user=User("mats", "xyzzy"),
                             machine=Linux(),
                             socket='/var/run/mysqld/mysqld.sock')

    def testConfig(self):
        "Test to get some configuration information from the server"
        self.assertEqual(self.server.host, "localhost")
        self.assertEqual(self.server.port, 3306)
        self.assertEqual(self.server.socket, '/var/run/mysqld/mysqld.sock')

    def testFetchReplace(self):
        self.server.fetch_config(os.path.join(here, 'test.cnf'))
        self.assertEqual(self.server.get_option('user'), 'mysql')
        self.assertEqual(self.server.get_option('log-bin'),
                         '/var/log/mysql/master-bin')
        self.assertEqual(self.server.get_option('slave-skip-start'), None)
        self.server.set_option('no-value')
        self.assertEqual(self.server.get_option('no-value'), None)
        self.server.set_option('with-int-value', 4711)
        self.assertEqual(self.server.get_option('with-int-value'), '4711')
        self.server.set_option('with-string-value',
                               'Careful with that axe, Eugene!')
        self.assertEqual(self.server.get_option('with-string-value'),
                         'Careful with that axe, Eugene!')
        self.server.replace_config(os.path.join(here, 'test-new.cnf'))
        lines1 = file(os.path.join(here, 'test.cnf')).readlines()
        lines2 = file(os.path.join(here, 'test-new.cnf')).readlines()
        lines1 += ["\n", "no-value\n", "with-int-value = 4711\n",
                   "with-string-value = Careful with that axe, Eugene!\n"]
        lines1.sort()
        lines2.sort()
        self.assertEqual(lines1, lines2)

        
    def testSsh(self):
        self.assertEqual(''.join(self.server.ssh(["echo", "-n", "Hello"])),
                         "Hello")
 
    def testSql(self):
        self.server.connect()
        self.assertEqual(self.server.sql("select 'Hello' as val")['val'],
                         "Hello")
 
def suite():
    return unittest.makeSuite(TestServerBasics, 'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

