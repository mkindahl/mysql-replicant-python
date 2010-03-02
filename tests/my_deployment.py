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


from replicant import Server, User, Linux, Master, Final
import time, os.path

class MultiLinux(Linux):
    """Class to handle the case where there are multiple servers
    running at the same box, all managed by mysqld_multi."""
    def __init__(self, number):
        self.__number = number

    def stop_server(self, server):
        server.ssh(["mysqld_multi", "stop", str(self.__number)])
        pidfile = ''.join("/var/run/mysqld", server.name, ".pid")
        while os.path.exists(pidfile):
            time.sleep(1)

    def start_server(self, server):
        import time
        print "Starting server...",
        server.ssh(["mysqld_multi", "start", str(self.__number)])
        time.sleep(1)           # Need some time for server to start
        print "done"

_replicant_user = User("mysql_replicant", "xyzzy")
_repl_user = User("repl_user", "xyzzy")

def _cnf(name):
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, name + ".cnf")

master = Server(server_id=1, name="mysqld1",
                sql_user=_replicant_user,
                ssh_user=User("mysql"),
                machine=Linux(), role=Master(_repl_user),
                port=3307,
                socket='/var/run/mysqld/mysqld1.sock',
                defaults_file=_cnf("mysqld1"),
                config_section="mysqld1")
slaves = [Server(server_id=2, name="mysqld2",
                 sql_user=_replicant_user,
                 ssh_user=User("mysql"),
                 machine=Linux(), role=Final(master),
                 port=3308,
                 socket='/var/run/mysqld/mysqld2.sock',
                 defaults_file=_cnf("mysqld2"),
                 config_section="mysqld2"),
          Server(server_id=3, name="mysqld3",
                 sql_user=_replicant_user,
                 ssh_user=User("mysql"),
                 machine=Linux(), role=Final(master),
                 port=3309,
                 socket='/var/run/mysqld/mysqld3.sock',
                 defaults_file=_cnf("mysqld3"),
                 config_section="mysqld3"),
          Server(server_id=4, name="mysqld4",
                 sql_user=_replicant_user,
                 ssh_user=User("mysql"),
                 machine=Linux(), role=Final(master),
                 port=3310,
                 socket='/var/run/mysqld/mysqld4.sock',
                 defaults_file=_cnf("mysqld4"),
                 config_section="mysqld4")]
servers = [master] + slaves
