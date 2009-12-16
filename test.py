#!/usr/bin/python

import unittest

def suite():
    import tests.basic
    import tests.server
    import tests.roles

    suite = unittest.TestSuite()
    suite.addTest(tests.basic.suite())
    suite.addTest(tests.roles.suite())
    suite.addTest(tests.server.suite())

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

