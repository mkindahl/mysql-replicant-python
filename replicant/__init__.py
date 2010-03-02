# Copyright (c) 2009-10, Sun Microsystems, Inc.
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

"""replicant - A library for working with deployments of MySQL servers.
"""

import os, re, subprocess, MySQLdb, ConfigParser

from configfile import *
from machine import *
from roles import *

class Error(BaseException):
    "Base class for all exceptions in this package"
    pass

class EmptyRowError(Error):
    "Class to handle attempts to fetch a key from an empty row."
    pass

class NotConnectedError(Error):
    "Exception raised when the server is not connected."
    pass

class NoOptionError(Error):
    "Exception raised when ConfigManager does not find the option"
    pass

class SlaveNotRunningError(Error):
    "Exception raised when slave is not running but were expected to run"
    pass

class NotMasterError(Error):
    """Exception raised when the server is not a master and the
    operation is illegal."""
    pass

class Position:
    """Class to represent a binlog position for a specific server."""
    def __init__(self, server_id=None, file='', pos=0):
        self.server_id = server_id
        self.file = file
        self.pos = pos

    def __cmp__(self, other):
        """Compare two positions lexicographically.  If the positions
        are from different servers, a ValueError exception will be
        raised.
        """
        if self.server_id != other.server_id:
            raise ValueError, "Positions are for different servers"
        else:
            return cmp((self.file, self.pos), (other.file, other.pos))

    def __repr__(self):
        "Give a printable and parsable representation of a binlog position"
        if self.pos == 0 or self.file == '':
            args = ''
        else:
            args = ', '.join([str(self.server_id), "'" + self.file + "'",
                              str(self.pos)])
        return "Position(" + args + ")"
            

class User(object):
    """A MySQL server user"""
    def __init__(self, name, passwd = ""):
        self.name = name
        self.passwd = passwd

    def __repr__(self):
        return ' '.join(['<', self.name, ',', self.passwd, '>'])


class Server(object):
    """A representation of a MySQL server.

    A server object is used as a proxy for operating with the
    server. The basic primitives include connecting to the server and
    executing SQL statements and/or shell commands."""

    class Row(object):
        """Class to represent a row (iterator) returned when executing
        an SQL statement. For statements that return a single row, the
        object can be treated as a row as well."""
        def __init__(self, cursor):
            self.__cursor = cursor
            self.__row = cursor.fetchone()

        def __iter__(self):
            return self

        def next(self):
            row = self.__row
            if row is None:
                raise StopIteration
            else:
                self.__row = self.__cursor.fetchone()
                return row
        
        def __getitem__(self, key):
            if self.__row is not None:
                return self.__row[key]
            else:
                raise EmptyRowError
    
    def __init__(self, name, sql_user, ssh_user, machine,
                 config_manager=ConfigManagerFile(), role=Vagabond(), 
                 server_id=None, host='localhost', port=3306,
                 socket='/tmp/mysqld.sock', defaults_file=None,
                 config_section='mysqld'):
        """Initialize the server object with data.

        If a configuration file path is provided, it will be used to
        read server options that were not provided. There are three
        mandatory options:

        sql_user

           This is a user for connecting to the server to execute SQL
           commands. This is a MySQL server user.

        ssh_user

           This is a user for connecting to the machine where the
           server is installed in order to perform tasks that cannot
           be done through the MySQL client interface.

        machine

           This is a machine object for performing basic operations on
           the server such as starting and stopping the server.

        The following additional keyword parameters are used:

        name

           This parameter is used to create names for the pid-file,
           log-bin, and log-bin-index options. If it is not provided,
           the name will be deduced from the pid-file, log-bin, or
           log-bin-index (in that order), or a default will be used.

        host

           The hostname of the server, which defaults to 'localhost',
           meaning that it will connect using the socket and not
           TCP/IP.

        socket

           Socket to use when connecting to the server. This parameter
           is only used if host is 'localhost'. It defaults to
           '/tmp/mysqld.sock'.

        port

           Port to use when connecting to the server when host is not
           'localhost'. It defaults to 3306.

        server_id

           Server ID to use. If none is assigned, the server ID is
           fetched from the configuration file. If the configuration
           files does not contain a server ID, no server ID is
           assigned.
        """

        if not defaults_file:
            defaults_file = machine.defaults_file

        self.name = name
        self.sql_user = sql_user
        self.ssh_user = ssh_user

        # These attributes are explicit right now, we have to
        # implement logic for fetching them from the configuration if
        # necessary.
        self.host = host
        self.port = port
        self.server_id = server_id
        self.socket = socket
        self.defaults_file = defaults_file
        
        self.config_section = config_section

        self.__machine = machine
        self.__config_manager = config_manager
        self.__role = role
        self.__conn = None
        self.__config = None
        self.__tmpfile = None

        self.__role.imbue(self)
            
    def connect(self, db=''):
        """Method to connect to the server, preparing for execution of
        SQL statements.  If a connection is already established, this
        function does nothing."""
        from MySQLdb import connect
        if not self.__conn:
            self.__conn = connect(host=self.host, port=self.port,
                                  unix_socket=self.socket, db=db,
                                  user=self.sql_user.name,
                                  passwd=self.sql_user.passwd)
                                      
    def disconnect(self):
        """Method to disconnect from the server."""
        self.__conn = None
                                      
    def sql(self, command, args=None):
        """Execute a SQL command on the server. This first requires a
        connection to the server.

        The function will return an iteratable to the result of the
        execution with one row per iteration.  The function can be
        used in the following way:

        for db in server.sql("SHOW DATABASES")
            print db["Database"]"""
        try:
            c = self.__conn.cursor(MySQLdb.cursors.DictCursor)
            c.execute(command, args)
            return Server.Row(c)
        except AttributeError:
            raise NotConnectedError

    def ssh(self, command):
        """Execute a shell command on the server.

        The function will return an iteratable (currently a list) to
        the result of the execution with one line of the output for
        each iteration.  The function can be used in the following
        way:

        for line in server.ssh(["ls"])
            print line

        For remote commands we do not allow X11 forwarding, and the
        stdin will be redirected to /dev/null."""
        from subprocess import Popen, PIPE

        if self.host == "localhost":
            cmd = ["sudo", "-u" + self.ssh_user.name] + command
            process = Popen(cmd, stdout=PIPE)
        else:
            fullname = self.ssh_user.name + "@" + self.host
            process = Popen(["ssh", "-fqTx", fullname, ' '.join(command)],
                            stdout=PIPE)
        output = process.communicate()[0]
        return output.split("\n")

    def replace_file(self, remote, local):
        """Function to put a file to a remote server."""
        import shutil, subprocess
        if self.host != "localhost":
            target = self.ssh_user.name + "@" + self.host + ":" + path
            process = subprocess.Popen(["scp", "-qB", local, target],
                                       stderr=subprocess.PIPE)
            err = process.communicate()[1]
        else:
            shutil.copyfile(local, remote)

    def fetch_config(self, path=None):
        return self.__config_manager.fetch_config(self, path)

    def replace_config(self, config, path=None):
        self.__config_manager.replace_config(self, config, path)

    def stop(self):
        self.__machine.stop_server(self)

    def start(self):
        self.__machine.start_server(self)


#
# Various utilities
#

def flush_and_lock_database(server):
    """Flush all tables and lock the database"""
    server.sql("FLUSH TABLES WITH READ LOCK")

def unlock_database(server):
    "Unlock database"
    server.sql("UNLOCK TABLES")

_CHANGE_MASTER_TO = """CHANGE MASTER TO
   MASTER_HOST=%s, MASTER_PORT=%s,
   MASTER_USER=%s, MASTER_PASSWORD=%s,
   MASTER_LOG_FILE=%s, MASTER_LOG_POS=%s"""

_CHANGE_MASTER_TO_NO_POS = """CHANGE MASTER TO
   MASTER_HOST=%s, MASTER_PORT=%s,
   MASTER_USER=%s, MASTER_PASSWORD=%s"""

def change_master(slave, master, position=None):
    """Configure replication to read from a master and position."""
    try:
        user = master.repl_user
    except AttributeError:
        raise NotMasterError

    slave.connect()
    slave.sql("STOP SLAVE")
    if position:
        slave.sql(_CHANGE_MASTER_TO,
                  (master.host, master.port, user.name, user.passwd,
                   position.file, position.pos))
    else:
        slave.sql(_CHANGE_MASTER_TO_NO_POS,
                  (master.host, master.port, user.name, user.passwd))
    slave.sql("START SLAVE")
    slave.disconnect()

def fetch_master_pos(server):
    """Get the position of the next event that will be written to
    the binary log"""
    try:
        result = server.sql("SHOW MASTER STATUS")
        return Position(server.server_id,
                        result["File"], result["Position"])
    except EmptyRowError:
        raise NotMasterError

def fetch_slave_pos(server):
    """Get the position of the next event to be read from the master"""
    result = server.sql("SHOW SLAVE STATUS")
    return Position(server.server_id,
                    result["Relay_Master_Log_File"],
                    result["Exec_Master_Log_Pos"])

_START_SLAVE_UNTIL = """START SLAVE UNTIL
    MASTER_LOG_FILE=%s, MASTER_LOG_POS=%s"""

_MASTER_POS_WAIT = "SELECT MASTER_POS_WAIT(%s, %s)"

def slave_wait_and_stop(slave, position):
    """Set up replication so that it will wait for the position to be
    reached and then stop replication exactly at that binlog
    position."""
    server.sql("STOP_SLAVE")
    server.sql(_START_SLAVE_UNTIL, (position.file, position.pos))
    server.sql(_MASTER_POS_WAIT, (position.file, position.pos))
    
def slave_wait_for_empty_relay_log(slave):
    result = server.sql("SHOW SLAVE STATUS");
    file = result["Master_Log_File"]
    pos = result["Read_Master_Log_Pos"]
    if server.sql(_MASTER_POS_WAIT, (file, pos)) is None:
        raise SlaveNotRunningError

def fetch_binlog(server, binlog_files=None,
                 start_datetime=None, stop_datetime=None):
    """Fetch the lines of a binary log remotely using the
    ``mysqlbinlog`` program.

    If no binlog file names are given, a connection to the server is
    made and a ``SHOW BINARY LOGS`` is executed to get a full list of
    the binary logs, which is then used.
    """
    from subprocess import Popen, PIPE
    if not binlog_files:
        binlog_files = [
            row["Log_name"] for row in server.sql("SHOW BINARY LOGS")]
    
    command = ["mysqlbinlog",
               "--read-from-remote-server",
               "--force",
               "--host=%s" % (server.host),
               "--user=%s" % (server.sql_user.name)]
    if server.sql_user.passwd:
        command.append("--password=%s" % (server.sql_user.passwd))
    if start_datetime:
        command.append("--start-datetime=%s" % (start_datetime))
    if stop_datetime:
        command.append("--stop-datetime=%s" % (stop_datetime))
    return iter(Popen(command + binlog_files, stdout=PIPE).stdout)

def clone(slave, source, master = None):
    """Function to create a new slave by cloning either a master or a
    slave."""
    backup_name = server.host + ".tar.gz"
    source.connect()
    if master is not None:
        source.sql("STOP SLAVE");
    lock_database(source)
    if master is None:
        position = fetch_master_position(source)
    else:
        position = fetch_slave_position(source)
    source.ssh("tar Pzcf " + backup_name + " /usr/var/mysql")
    if master is not None:
        source.sql("START SLAVE")
    subprocess.call(["scp", source.host + ":" + backup_name, slave.host + ":."])
    slave.ssh("tar Pzxf " + backup_name + " /usr/var/mysql")
    if master is None:
        change_master(slave, source, position)
    else:
        change_master(slave, master, position)
    slave.sql("START SLAVE")

_START_SLAVE_UNTIL = "START SLAVE UNTIL MASTER_LOG_FILE=%s, MASTER_LOG_POS=%s"
_MASTER_POS_WAIT = "SELECT MASTER_POS_WAIT(%s,%s)"

def replicate_to_position(server, pos):
    """Run replication until it reaches 'pos'.

    The function will block until the slave have reached the position."""
    server.sql(_START_SLAVE_UNTIL, (pos.file, pos.pos))
    server.sql(_MASTER_POS_WAIT, (pos.file, pos.pos))
