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
rootpath = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
sys.path.append(rootpath) 

import MySQLdb, replicant, my_deployment

class AlreadyInPoolError(replicant.Error):
    pass

class NotInPoolError(replicant.Error):
    pass

_INSERT_SERVER = """
INSERT INTO nodes(host, port, sock, type)
    VALUES (%s, %s, %s, %s)"""

_DELETE_SERVER = "DELETE FROM nodes WHERE host = %s AND port = %s"

_UPDATE_SERVER = "UPDATE nodes SET type = %s WHERE host = %s AND port = %s"

def pool_add(common, server, type=[]):
    try:
        common.sql(_INSERT_SERVER,
                   (server.host, server.port, server.socket, ','.join(type)),
                   db="common");
    except MySQLdb.IntegrityError:
        raise AlreadyInPoolError


def pool_del(common, server):
    common.sql(_DELETE_SERVER, (server.host, server.port), db="common")

def pool_set(common, server, type):
    common.sql(_UPDATE_SERVER, (','.join(type), server.host, server.port),
               db="common")

import unittest
    
class TestLoadBalancer(unittest.TestCase):
    "Class to test the load balancer functions."

    def setUp(self):
        from my_deployment import common, master, slaves
        try:
            pool_add(common, master, ['READ', 'WRITE'])
        except AlreadyInPoolError:
            pool_set(common, master, ['READ', 'WRITE'])

        for slave in slaves:
            try:
                pool_add(common, slave, ['READ'])
            except AlreadyInPoolError:
                pool_set(common, slave, ['READ'])

    def tearDown(self):
        from my_deployment import common, servers
        for server in servers:
            pool_del(common, server)

    def testServers(self):
        from my_deployment import common, master, slaves
        for row in common.sql("SELECT * FROM nodes", db="common"):
            if row['port'] == master.port:
                self.assertEqual(row['type'], 'READ,WRITE')
            elif row['port'] in [slave.port for slave in slaves]:
                self.assertEqual(row['type'], 'READ')

if __name__ == '__main__':
    unittest.main()
    

