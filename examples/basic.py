import sys, os.path
rootpath = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
sys.path.append(rootpath)

import mysqlrep, my_deployment

my_deployment.master.connect()

print "# Executing 'show databases'"
for db in my_deployment.master.sql("show databases"):
    print db["Database"]

print "# Executing 'ls'"
for line in my_deployment.master.ssh(["ls"]):
    print line

print "Master position is:", mysqlrep.fetch_master_pos(my_deployment.master)

try:
    print mysqlrep.fetch_slave_pos(my_deployment.master)
except mysqlrep.EmptyRowError:
    print "Not configured as a slave"
