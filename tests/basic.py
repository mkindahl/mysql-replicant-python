import sys, os.path
rootpath = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
sys.path.append(rootpath) 

import unittest
import mysqlrep

class TestPosition(unittest.TestCase):
    "Test case for binlog positions class."
    def _checkPos(self, p, s):
        """Check that a position is valid, have the expected
        representation, and can be converted from string
        representation to class and back."""
        from mysqlrep import Position
        self.assertEqual(repr(p), s)
        self.assertEqual(p, eval(repr(p)))
        self.assertEqual(s, repr(eval(s)))
        
    def testSimple(self):
        from mysqlrep import Position
        positions = [Position(1, 'master-bin.00001', 4711),
                     Position(1, 'master-bin.00001', 9393),
                     Position(1, 'master-bin.00002', 102)]
        strings = ["Position(1, 'master-bin.00001', 4711)",
                   "Position(1, 'master-bin.00001', 9393)",
                   "Position(1, 'master-bin.00002', 102)"]
 
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

    def testExcept(self):
        try:
            pos = [mysqlrep.Position(1,'master-bin.00001',4711),
                   mysqlrep.Position(2,'master-bin.00001',4780)] 
            result = (pos[0] < pos[1])
        except ValueError, e:
            pass
        else:
            fail("Expected ValueError")


def suite():
    return unittest.makeSuite(TestPosition)

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
