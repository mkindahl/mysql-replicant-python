from mysqlrep import Server, User, Linux

servers = [Server(sql_user=User("mats"),
                  ssh_user=User("mats", "xyzzy"),
                  machine=Linux(),
                  socket='/var/run/mysqld/mysqld.sock')]
master = servers[0]
slaves = servers[1:]
