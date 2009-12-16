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
