#! /usr/bin/env python
# -*- coding: utf-8 -*-

import cmd2
import sys
import argparse
import MySQLdb
import psycopg2
import _mysql_exceptions
import ConfigParser
import getpass
import logging
import commands
import copy

from EngineMySQL import *
from EnginePostgres import *

logging.basicConfig(level=logging.FATAL)


class Console(cmd2.Cmd):

    version = '0.1'
    prompt = ''
    cursor = ''
    connection = ''
    args = ''
    default_args = ''
    connection_data = {'host': '', 'user': '',
                       'database': '', 'port': 3306, 'conn': '',
                       'engine': ''}
    connections = {}
    stored_conn = ''
    databases = []
    tables = []
    columns = []
    terminators = [';', '\G', '\g']
    multilineCommands = ['ALTER', 'ANALYZE', 'CREATE', 'DELETE', 'DESC',
                         'EXPLAIN', 'INSERT', 'SELECT', 'SHOW',
                         'UPDATE', 'USE']
    saved_queries_file = 'saved_queries.txt'
    saved_queries = []

    def __init__(self):
        """Constructor"""

        cmd2.Cmd.__init__(self)
        self.arguments()

        # Custom settings if you don't have set up in .config file
        self.color_config_dict = {'borders': 'red', 'borders_bold': 'True',
                                  'result': None, 'result_bold': 'False'}
        self.colors = ('red', 'cyan', 'green', 'magenta', 'blue')
        self.color_config = ConfigParser.ConfigParser()
        self.color_config.read('.config')

        _color = self.color_config.get('colors', "borders",
                                       vars=self.color_config_dict)
        _borders_bold = self.color_config.get('colors', "borders_bold",
                                              vars=self.color_config_dict)
        _result = self.color_config.get('colors', "result",
                                        vars=self.color_config_dict)
        _result_bold = self.color_config.get('colors', "result_bold",
                                             vars=self.color_config_dict)
        self.color_config_dict['borders'] = _color
        self.color_config_dict['borders_bold'] = _borders_bold
        self.color_config_dict['result'] = _result
        self.color_config_dict['result_bold'] = _result_bold
        self.get_stored_connections()

        # Se instalan los comandos (tipo plugins)
        commands.Select().install(self)
        commands.Insert().install(self)
        commands.Show().install(self)
        commands.Drop().install(self)
        commands.Use().install(self)
        commands.Desc().install(self)

    def arguments(self):
        """
        Parse arguments
        """
        parser = argparse.ArgumentParser(description='Connect to a MySQL\
                                         server')
        parser.add_argument("-u", "--user", dest='user',
                            help="The MySQL user name to use when connecting\
                            to the server.")
        parser.add_argument("-p", "--password", dest='password',
                            help="The password to use when connecting \
                            to the server.")

        parser.add_argument("-hs", "--host", dest='host',
                            help="Connect to the MySQL server on the \
                            given host.")

        parser.add_argument("-D", "--database", dest='database',
                            help="Database name.")

        parser.add_argument("-P", "--port", dest='port',
                            help="The TCP/IP port number to use for \
                            the connection.")

        parser.add_argument("-e", "--engine", dest='engine',
                            help="SQL Engine: MySQL, PostgreSQL")

        parser.add_argument("-cnt", "--connection", dest='connection',
                            help="Select a conection saved in\
                            .connections file")

        self.args = parser.parse_args()
        if(self.args.connection is None):
            self.default_args = copy.copy(self.args)

        self.get_welcome()
        self.connect(self.args)

    def connect(self, args):
        """
        This method is for connect to the database
        """

        if(args.user is not None and args.connection is None):

            if(args.password is None):
                db_pass = getpass.getpass()
            else:
                db_pass = args.password
            if(args.host is None):
                db_host = 'localhost'
            else:
                db_host = args.host
            if(args.database is None):
                db = ''
            else:
                db = args.database
            if(args.port is None):
                db_port = 3306
            else:
                db_port = args.port

            try:
                if('default' not in self.connections):
                    self.connection = MySQLdb.connect(host=db_host,
                                                      user=args.user,
                                                      passwd=db_pass,
                                                      db=db,
                                                      port=db_port)
                    self.cursor = self.connection.cursor()
                else:
                    self.cursor = self.connections['default']

                self.mysql_server_info()
                self.connection_data['host'] = db_host
                self.connection_data['user'] = args.user
                self.connection_data['database'] = db
                self.connection_data['port'] = db_port
                self.connection_data['conn'] = 'default'
                self.connections['default'] = self.cursor
                self.prompt = self.get_prompt(self.connection_data['user'],
                                              self.connection_data['host'],
                                              self.connection_data['database'])

                self.get_databases()
                self.get_tables(str(self.connection_data['database']))
                self.get_columns(str(self.connection_data['database']))
                self.get_saved_queries()
            except:
                sys.exit(u"Access denied for user '%s'@'%s'" %
                         (self.connection_data['user'],
                          self.connection_data['host']))

        elif(args.connection is not None):
            self.get_stored_connections()

            self.connection_data['user'] =\
            self.stored_conn.get(args.connection, "user")

            self.connection_data['host'] =\
            self.stored_conn.get(args.connection, "host")

            self.connection_data['database'] =\
            self.stored_conn.get(args.connection, "database")

            self.connection_data['conn'] = args.connection

            self.connection_data['port'] =\
            self.stored_conn.get(args.connection, "port")

            self.connection_data['engine'] =\
            self.stored_conn.get(args.connection, "engine")

            try:
                self.connection_data['port'] =\
                self.stored_conn.get(args.connection, 'port')
            except:
                pass

            try:
                if(args.connection not in self.connections):
                    db_pass = getpass.getpass()
                    self.engine_connect(self.connection_data, db_pass)
                else:
                    self.cursor = self.connections[args.connection]

                self.prompt = self.get_prompt(self.connection_data['user'],
                                              self.connection_data['host'],
                                              self.connection_data['database'])
                self.get_saved_queries()
            except:
                sys.exit(u"Access denied for user '%s'@'%s'"
                         % (self.connection_data['user'],
                            self.connection_data['host']))
        else:
            sys.exit(u"Please, use -h option to know about how to use TOMy")

    def engine_connect(self, conn_data, db_passwd):
        """
        """
        db_engine = conn_data['engine']
        db_user = conn_data['user']
        db_host = conn_data['host']
        db_db = conn_data['database']
        db_port = int(conn_data['port'])

        if(db_engine == 'postgres'):
            self.connection = psycopg2.connect(user=db_user,
                                               password=db_passwd,
                                               database=db_db,
                                               port=db_port,
                                               host=db_host)
            self.cursor = self.connection.cursor()
            self.connections[conn_data['conn']] = self.cursor
            self.postgres_server_info()

        elif(db_engine == 'mysql'):
            self.connection = MySQLdb.connect(host=db_host,
                                              user=db_user,
                                              passwd=db_passwd,
                                              db=db_db,
                                              port=db_port)
            self.cursor = self.connection.cursor()
            self.connections[conn_data['conn']] = self.cursor
            self.mysql_server_info()
            a = EngineMySQL()
            self.databases = EngineMySQL.get_databases(a, self.cursor)
            self.tables = EngineMySQL.get_tables(a, self.cursor, db_db)
            self.columns = EngineMySQL.get_columns(a, self.cursor, db_db)

    def get_prompt(self, user, host, database='None'):
        """
        Get a prompt
        """
        # Custom settings if you don't have set up in .config file
        prompt_config_dict = {'show_user': False, 'show_host': False,
                              'show_db': False, 'prompt_char': '>>>'}

        self.connection_data['host'] = host
        self.connection_data['user'] = user
        self.connection_data['database'] = database
        if(user == 'root'):
            user = self.colorize(user, 'red')
            user = self.colorize(user, 'bold')

        try:
            prompt_config = ConfigParser.ConfigParser()
            prompt_config.read('.config')
            prompt_config_dict['show_user'] = prompt_config.get('prompt',
                                                                "show_user")
            prompt_config_dict['show_host'] = prompt_config.get('prompt',
                                                                "show_host")
            prompt_config_dict['show_db'] = prompt_config.get('prompt',
                                                              "show_db")

            prompt_config_dict['prompt_char'] = prompt_config.get('prompt',
                                                                "prompt_char")
        except:
            # TODO: use exceptions in a decent way
            logging.error('Wrong section definition')

        prompt = 'conn: %s\n' % self.connection_data['conn']
        if(prompt_config_dict['show_user'] == 'True'):
            if(prompt_config_dict['show_host'] == 'True'):
                prompt = '%s<%s@%s>' % (prompt, user, host)
            else:
                prompt = '%s<%s>' % (prompt, user)
        else:
            if(prompt_config_dict['show_host'] == 'True'):
                prompt = '%s<%s>' % (prompt, host)
            else:
                pass

        if(prompt_config_dict['show_db'] == 'True'):
            prompt = '%s [%s] ' % (prompt, database)

        prompt = prompt + prompt_config_dict['prompt_char'] + ' '

        return prompt

    def mysql_server_info(self):
        """
        Shows the server info
        """
        a = EngineMySQL()
        b = EngineMySQL.server_info(a, self.connection)
        server_info = b[0]
        server_status = b[1]
        server_connection_id = b[2]
        print '.:: Server version: %s'\
            % (self.colorize(server_info, 'green'))
        print '.:: Server status: %s'\
            % (self.colorize(server_status, 'green'))
        print '.:: Server connection id: %s \n'\
            % (self.colorize(str(server_connection_id), 'green'))

    def postgres_server_info(self):
        """
        Shows the server info
        """
        a = EnginePostgres()
        b = EnginePostgres.server_info(a, self.connection)
        server_version = b[0]
        server_pid = b[1]
        print '.:: Server version: %s'\
            % (self.colorize(server_version, 'green'))
        print '.:: Server connection id: %s \n'\
            % (self.colorize(str(server_pid), 'green'))

    def get_welcome(self):
        """
        """
        welcome = '.:: Welcome to TOMy %s!' % (self.version)
        print welcome

    def get_saved_queries(self):
        """
        Get saved queries from saved_queries.txt file
        """
        saved_queries = ConfigParser.ConfigParser()
        saved_queries.read(self.saved_queries_file)
        self.saved_queries = []

        for sq in saved_queries.items('queries'):
            self.saved_queries.append(sq[0])

    def default(self, s):
        """
        Override the superclass method default to get the imput
        """

        query = s

        try:
            self.cursor.execute(query)
            header = self.cursor.description
            result = self.cursor.fetchall()

            if(header is not None):
                self.format_output(header, result)

            rows_count = self.cursor.rowcount
            rows_modified = self.connection.info()

            if(rows_modified is not None):
                print rows_modified + '\n'
                #TODO: Is this the best site to do this?
                self.connection.autocommit(True)
            else:
                print str(rows_count) + ' rows\n'

        except (_mysql_exceptions.DataError,
                _mysql_exceptions.IntegrityError,
                _mysql_exceptions.MySQLError,
                _mysql_exceptions.ProgrammingError,
                _mysql_exceptions.DatabaseError,
                _mysql_exceptions.InterfaceError,
                _mysql_exceptions.NotSupportedError,
                _mysql_exceptions.Warning,
                _mysql_exceptions.Error,
                _mysql_exceptions.InternalError,
                _mysql_exceptions.OperationalError), e:

            print self.colorize(self.colorize('\nERROR ' + str(e[0]),
                                'bold') + ': ' + e[1] +
                                '\n', 'red')

    do_ = default

    def get_stored_connections(self):
        """
        """
        self.stored_conn = ConfigParser.ConfigParser()
        self.stored_conn.read(".connections")

    def do_connect(self, conn_name):
        """
        Connect to another MySQL server.
        The connection data must be stored in .connections file
        """
        if(conn_name == 'default' and self.default_args is not None):
            self.connect(self.default_args)
        else:
            self.args.connection = conn_name
            self.connect(self.args)

    def complete_connect(self, text, line, begidx, endidx):
        """
        Completions for connect command
        """
        candidates = self.stored_conn.sections()
        completions = [d for d in candidates if d.startswith(text)]
        return completions

    def do_quit(self, s):
        print "Good Bye!!!"
        self.connection.close()
        return True
    do_exit = do_quit

    def help_quit(self):
        print "Quits the console"

    def do_save_query(self, stm):
        """
        Saves the last excecuted query:
        save_query [name]
        """
        guardar = self.history[len(self.history) - 2]
        saved_queries = ConfigParser.ConfigParser()
        saved_queries.read(self.saved_queries_file)
        saved_queries.set('queries', stm, guardar)

        with open(self.saved_queries_file, 'wb') as f:
            saved_queries.write(f)

        self.get_saved_queries()
        print "\n"

    def do_recover_query(self, stm):
        """
        Recover a saved query
        recover_query [name]
        """
        saved_queries = ConfigParser.ConfigParser()
        saved_queries.read(self.saved_queries_file)
        print saved_queries.get('queries', stm) + "\n"

    def do_remove_query(self, stm):
        """
        Remove save query
        remove_query [name]
        """
        saved_queries = ConfigParser.ConfigParser()
        saved_queries.read(self.saved_queries_file)
        saved_queries.remove_option('queries', stm)

        with open(self.saved_queries_file, 'wb') as f:
            saved_queries.write(f)
            print "Removed query: " + stm + "\n"

        self.get_saved_queries()

    def complete_saved_queries(self, text, line, begidx, endidx):
        """
        """
        if not text:
            completions = self.saved_queries[:]
        else:
            completions = [d for d in self.saved_queries if d.startswith(text)]
        return completions

    complete_remove_query = complete_saved_queries
    complete_recover_query = complete_saved_queries

    def format_output(self, headers_tuple, result):
        """
        This method formats the query output
        Code inspired in http://code.activestate.com/recipes/\
                577202-render-tables-for-text-interface/
        """

        column_names = list()
        rows = list(result)

        for h in headers_tuple:
            column_names.append(h[0])

        headers = column_names
        fieldlen = []

        ncols = len(headers)

        for i in range(ncols):
            _max = 0
            for j in rows:
                if len(str(j[i])) > _max:
                    _max = len(str(j[i]))
            fieldlen.append(_max)

        for i in range(len(headers)):
            if len(str(headers[i])) > fieldlen[i]:
                fieldlen[i] = len(str(headers[i]))

        width = sum(fieldlen) + (ncols - 1) * 3 + 4

        bar = "-" * (width - 2)
        bar = "+" + bar + "+"
        pipe = '|'

        if(self.color_config_dict['borders'] in self.colors):
            bar = self.colorize(bar, self.color_config_dict['borders'])
            pipe = self.colorize(pipe, self.color_config_dict['borders'])

        if(self.color_config_dict['borders_bold'] == 'True'):
            bar = self.colorize(bar, 'bold')
            pipe = self.colorize(pipe, 'bold')

        out = [bar]
        header = ""
        for i in range(len(headers)):
            header += pipe + " %s" % self.colorize((str(headers[i])), 'bold')\
                + " " * (fieldlen[i] - len(str(headers[i]))) + " "
        header += pipe
        out.append(header)
        out.append(bar)
        for i in rows:
            line = ""
            for j in range(len(i)):
                if(self.color_config_dict['result'] in self.colors):
                    r = self.colorize(str(i[j]),
                                      self.color_config_dict['result'])
                else:
                    r = str(i[j])

                if(self.color_config_dict['result_bold'] == 'True'):
                    r = self.colorize(r, 'bold')

                if(self.is_number(str(i[j])) is True):
                    line += pipe + " " * (fieldlen[j] - len(str(i[j]))) +\
                        " %s " % r
                else:
                    line += pipe + " %s" % r + " " * (fieldlen[j] -
                                                      len(str(i[j]))) + " "
            out.append(line + pipe)

        out.append(bar)
        print "\r\n".join(out)

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    do_EOF = do_quit
    help_EOF = help_quit

    def cmdloop(self):
        self._cmdloop()

if __name__ == "__main__":
    console = Console()
    try:
        console.cmdloop()
    except KeyboardInterrupt:
        console.do_quit(None)
