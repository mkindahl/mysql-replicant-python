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
here = os.path.dirname(os.path.abspath(__file__))
rootpath = os.path.split(here)[0]
sys.path.append(rootpath) 

import unittest
import replicant

def config_file(name):
    return os.path.join(here, name)
    
class TestConfigFile(unittest.TestCase):
    "Test case for the ConfigFile class."

    def testBasic(self):
        "Basic tests that a config file can be loaded"
        from replicant import ConfigManagerFile

        config = ConfigManagerFile.Config(path=config_file('test.cnf'),
                                          section='mysqld1')

        self.assertEqual(config.get('user'), 'mysql')
        self.assertEqual(config.get('log-bin'),
                         '/var/log/mysql/master-bin')
        self.assertEqual(config.get('slave-skip-start'), None)

    def testFetchReplace(self):
        "Fetching a configuration file, adding some options, and replacing it"

        from replicant import ConfigManagerFile

        config = ConfigManagerFile.Config(path=config_file('test.cnf'),
                                          section='mysqld1')

        config.set('no-value')
        self.assertEqual(config.get('no-value'), None)

        config.set('with-int-value', 4711)
        self.assertEqual(config.get('with-int-value'), '4711')

        config.set('with-string-value', 'Careful with that axe, Eugene!')
        self.assertEqual(config.get('with-string-value'),
                         'Careful with that axe, Eugene!')

        config.write(os.path.join(here, 'test-new.cnf'))
        lines1 = file(config_file('test.cnf')).readlines()
        lines2 = file(os.path.join(here, 'test-new.cnf')).readlines()
        lines1 += ["\n", "no-value\n", "with-int-value = 4711\n",
                   "with-string-value = Careful with that axe, Eugene!\n"]
        lines1.sort()
        lines2.sort()
        self.assertEqual(lines1, lines2)
        os.remove(os.path.join(here, 'test-new.cnf'))

def suite():
    return unittest.makeSuite(TestConfigFile, 'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

    
