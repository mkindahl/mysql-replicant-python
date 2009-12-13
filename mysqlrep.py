"""mysqlrep - A library for working with deployments of MySQL servers.
"""

__all__ = ["NotConnectedError", "EmptyRowError"]

import os, re, subprocess, MySQLdb, ConfigParser

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

class Position:
    """Class to represent a binlog position for a specific server."""
    def __init__(self, server_id, file, pos):
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
        args = str(self.server_id) + ", '" + self.file + "', " + str(self.pos)
        return "Position(" + args + ")"

class User(object):
    """A MySQL server user"""
    def __init__(self, name, passwd = ""):
        self.name = name
        self.passwd = passwd

    def __repr__(self):
        return ' '.join(['<', self.name, ',', self.passwd, '>'])


class Machine(object):
    """Base class for all machines. This hold primitives for
    accomplishing tasks on different hosts."""
    pass

class Linux(Machine):
    """Class holding operating system specific methods for (Debian)
    Linux."""
    default_config_path = "/etc/mysql/my.cnf"

    def stop_server(self, server):
        server.ssh("/etc/init.d/mysql stop")

    def start_server(self, server):
        server.ssh("/etc/init.d/mysql start")


class Solaris(Machine):
    """Class holding operating system specific methods for Solaris."""
    default_config_path = "/etc/mysql/my.cnf"

    def stop_server(self, server):
        server.ssh("/etc/sbin/svcadm disable mysql")

    def start_server(self, server):
        server.ssh("/etc/sbin/svcadm enable mysql")


_NONE_MARKER = "<>"

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
    
    def __init__(self, machine, sql_user, ssh_user,
                 host='localhost', port=3306, socket='/tmp/mysqld.sock',
                 config_section='mysqld', config_path=None):
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

        from ConfigParser import SafeConfigParser

        self.sql_user = sql_user
        self.ssh_user = ssh_user
        self.host = host
        self.port = port
        self.socket = socket

        if config_path is None:
            config_path = machine.default_config_path

        self.__machine = machine
        self.__conn = None
        self.__config = SafeConfigParser()
        self.__tmpfile = None
        self.__config_path = config_path
        self.__config_section = config_section
            
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

    def fetch_file(self, remote, local):
        """Function to fetch a file from the server and copy it to the
        local machine."""
        import subprocess, shutil

        if self.host != "localhost":
            source = self.ssh_user.name + "@" + self.host + ":" + remote
            subprocess.check_call(["scp", "-qB", source, local])
        else:
            shutil.copyfile(remote, local)

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

    def stop(self):
        self.__machine.stop_server(self)

    def start(self):
        self.__machine.start_server(self)

    def _fetch_config_file(self, config_path=None):
        from tempfile import mkstemp
        assert not self.__tmpfile
        if not config_path:
            config_path = self.__config_path
        handle, file = mkstemp(text=True)
        os.close(handle)
        self.fetch_file(config_path, file)
        self.__tmpfile = file

    def _replace_config_file(self, config_path=None):
        if not config_path:
            config_path = self.__config_path
        self.replace_file(config_path, self.__tmpfile)
        os.remove(self.__tmpfile)
        self.__tmpfile = None

    def _clean_config_file(self):
        input = file(self.__tmpfile, 'r')
        lines = input.readlines()
        input.close()

        output = file(self.__tmpfile, 'w')
        for line in lines:
            if re.match("#.*|\[\w+\]|[\w\d_-]+\s*=\s*.*", line):
                pass
            elif re.match("\s*[\w\d_-]+\s*", line):
                line = ''.join([line.rstrip("\n"), " = ", _NONE_MARKER, "\n"])
            else:
                line = "#!#" + line
            output.write(line)
        output.close()

    def _unclean_config_file(self):
        input = file(self.__tmpfile, 'r')
        lines = input.readlines()
        input.close()

        output = file(self.__tmpfile, 'w')
        for line in lines:
            m = re.match("([\w\d_-]+)\s*=\s*(.*)", line)
            if m and m.group(2) == _NONE_MARKER:
                output.write(m.group(1) + "\n")
                continue
            if re.match("#!#.*", line):
                output.write(line[3:])
                continue
            output.write(line)
        output.close()

    def fetch_config(self, config_path=None):
        """Method to fetch the configuration options from the server
        into memory.

        The method operates by creating a temporary file to which it
        copies the settings. Once the config settings are replaced,
        the temporary file is removed and to edit the options again,
        it is necessary to fetch the file again."""
        
        # We use ConfigParser, but since it cannot read configuration
        # files we options without values, we have to clean the output
        # once it is fetched before calling ConfigParser
        self._fetch_config_file(config_path)
        self._clean_config_file()
        self.__config.read(self.__tmpfile)

    def replace_config(self, config_path=None):
        """Method to replace the configuration file with the options
        in this object."""
        output = file(self.__tmpfile, 'w')
        self.__config.write(output)
        output.close()

        # Since ConfigParser cannot handle options without values
        # (yet), we have to unclean the file before replacing it.
        self._unclean_config_file()
        self._replace_config_file(config_path)

    def get_option(self, option):
        """Method to get the value of an option."""
        value = self.__config.get(self.__config_section, option)
        if value == _NONE_MARKER:
            value = None
        return value

    def set_option(self, option, value=None):
        """Method to set the value of an option. If set to None, the
        option is created but will not be given a value."""
        if value is None:
            value = _NONE_MARKER
        self.__config.set(self.__config_section, option, str(value))
