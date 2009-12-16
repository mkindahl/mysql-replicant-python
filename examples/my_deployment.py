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

from mysqlrep import Server, User, Linux

servers = [Server(server_id=1,
                  sql_user=User("mysql_replicant", "xyzzy"),
                  ssh_user=User("mats"),
                  machine=Linux(),
                  port=3307,
                  socket='/var/run/mysqld/mysqld1.sock',
                  config_path='/etc/mysql/mysqld1.cnf',
                  config_section='mysqld1'),
           Server(server_id=2,
                  sql_user=User("mysql_replicant", "xyzzy"),
                  ssh_user=User("mats"),
                  machine=Linux(),
                  port=3308,
                  socket='/var/run/mysqld/mysqld2.sock',
                  config_path='/etc/mysql/mysqld2.cnf',
                  config_section='mysqld2'),
           Server(sql_user=User("mysql_replicant", "xyzzy"),
                  ssh_user=User("mats"),
                  machine=Linux(),
                  port=3309,
                  socket='/var/run/mysqld/mysqld3.sock',
                  config_path='/etc/mysql/mysqld3.cnf',
                  config_section='mysqld3'),
           Server(sql_user=User("mysql_replicant", "xyzzy"),
                  ssh_user=User("mats"),
                  machine=Linux(),
                  port=3310,
                  socket='/var/run/mysqld/mysqld4.sock',
                  config_path='/etc/mysql/mysqld4.cnf',
                  config_section='mysqld4')]
master = servers[0]
slaves = servers[1:]
