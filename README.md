# MySQL Python Replicant

The MySQL Python Replicant is a library for controlling and
maintaining large deployments of MySQL servers. The library provide an
API to be able to fetch data from server, redirect slave servers, and
in general control the replication setup.


## Testing

The following command will execute the tests for the library.

    python setup.py test

The test suite currently does *not* use a mock database connection, so
for the server tests to work, you have to have a set of database
servers configured.

I have done the following to set up four servers on my local machine:

1. Edit /etc/mysql/my.cnf and adding the following lines:

        [mysqld_multi]
	    mysqladmin      = /usr/bin/mysqladmin
		user            = root

		[mysqld1]
		!include /etc/mysql/mysqld1.cnf
		[mysqld2]
		!include /etc/mysql/mysqld2.cnf
		[mysqld3]
		!include /etc/mysql/mysqld3.cnf
		[mysqld4]
		!include /etc/mysql/mysqld4.cnf

   The section headers are necessary for mysql_multi to recognize the
   servers.

2. Create one configuration file for each server, for example:

		[mysqld1]
		server-id       = 1
		pid-file        = /var/run/mysqld/mysqld1.pid
		socket          = /var/run/mysqld/mysqld1.sock
		port            = 3307
		datadir         = /var/lib/mysql1
		log-bin         = /var/lib/mysql1/mysqld1-bin.log
		log-bin-index   = /var/lib/mysql1/mysqld1-bin.index
   
3. Start the servers.

        $ sudo -umysql mysqld_multi start

4. Edit the `<root>/tests/my_deployment.py` file so that the information
   is correct.

5. Run the tests.


If you have apparmor active (I had), you have to edit the apparmor
file to avoid an error. I did the following change to
`/etc/apparmor.d/usr.sbin.mysqld`:

    --- usr.sbin.mysqld.orig        2010-07-04 09:16:51.218593117 +0200
    +++ usr.sbin.mysqld     2010-07-04 09:16:14.286592607 +0200
    @@ -23,6 +23,7 @@
       /etc/mysql/conf.d/ r,
       /etc/mysql/conf.d/* r,
       /etc/mysql/my.cnf r,
    +  /etc/mysql/mysqld[0-9].cnf, r
       /usr/sbin/mysqld mr,
       /usr/share/mysql/** r,
       /var/log/mysql.log rw,
    @@ -33,6 +34,14 @@
       /var/log/mysql/* rw,
       /var/run/mysqld/mysqld.pid w,
       /var/run/mysqld/mysqld.sock w,
    +  /var/log/mysql[1-9].log rw,
    +  /var/log/mysql[1-9].err rw,
    +  /var/lib/mysql[1-9]/ r,
    +  /var/lib/mysql[1-9]/** rwk,
    +  /var/log/mysql[1-9]/ r,
    +  /var/log/mysql[1-9]/* rw,
    +  /var/run/mysqld/mysqld[1-9].pid w,
    +  /var/run/mysqld/mysqld[1-9].sock w,

       /sys/devices/system/cpu/ r,
     }


## Installation

To install the library

    python setup.py install

## Licence

The MySQL Replicant is distributed under Apache License Version
2.0. See LICENCE file for more information.
