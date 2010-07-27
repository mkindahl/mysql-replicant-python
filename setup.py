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

import distutils.core, unittest, os

class TestCommand(distutils.core.Command):
    user_options = [ ]

    def initialize_options(self):
        self._dir = os.getcwd()

    def finalize_options(self):
        pass

    def run(self):
        "Finds all the tests modules in tests/, and runs them."

        import tests.config, tests.basic, tests.server, tests.roles
        import tests.commands, tests.backup, tests.binlog_reader

        suite = unittest.TestSuite()
        suite.addTest(tests.config.suite())
        suite.addTest(tests.basic.suite())
        suite.addTest(tests.roles.suite())
        suite.addTest(tests.server.suite())
        suite.addTest(tests.commands.suite())
        suite.addTest(tests.backup.suite())
        suite.addTest(tests.binlog_reader.suite())
        runner = unittest.TextTestRunner(verbosity=1)
        runner.run(suite)

distutils.core.setup(
    name='mysql-replicant',
    version='0.1.0',
    description='Package for controlling servers in a replication deployment',
    author='Mats Kindahl',
    author_email='mats@kindahl.net',
    url="http://launchpad.net/mysql-replicant-python",
    packages=['replicant'],
    classifiers=[
        'Programming Language :: Python',
    ],
    cmdclass = { 'test': TestCommand },
)
