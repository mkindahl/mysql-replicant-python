from mysqlrep import Server, User, Linux

servers = [Server(server_id=1,
                  sql_user=User("mysql_replicant", "xyzzy"),
                  ssh_user=User("mats"),
                  machine=Linux(),
                  port=3307,
                  socket='/var/run/mysqld/mysqld1.sock'),
           Server(sql_user=User("mysql_replicant", "xyzzy"),
                  ssh_user=User("mats"),
                  machine=Linux(),
                  port=3308,
                  socket='/var/run/mysqld/mysqld2.sock'),
           Server(sql_user=User("mysql_replicant", "xyzzy"),
                  ssh_user=User("mats"),
                  machine=Linux(),
                  port=3309,
                  socket='/var/run/mysqld/mysqld3.sock'),
           Server(sql_user=User("mysql_replicant", "xyzzy"),
                  ssh_user=User("mats"),
                  machine=Linux(),
                  port=3310,
                  socket='/var/run/mysqld/mysqld4.sock')]
master = servers[0]
slaves = servers[1:]
