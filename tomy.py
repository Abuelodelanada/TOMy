#! /usr/bin/env python
# -*- coding: utf-8 -*-

import cmd2
import sys
import argparse
import MySQLdb
import _mysql_exceptions
import ConfigParser
import getpass
import logging
import commands

logging.basicConfig(level=logging.FATAL)


class Console(cmd2.Cmd):

    prompt = ''
    cursor = ''
    connection = ''
    connection_data = {'host': '', 'user': '', 'database': '', 'port': 3306}
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

        # Se instalan los comandos (tipo plugins)
        commands.Select().install(self)
        commands.Insert().install(self)
        commands.Show().install(self)
        commands.Drop().install(self)

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
                            to the server. If you use the short option \
                            form (-p), you cannot have a space between \
                            the option and the password. If you omit the \
                            password value following the --password or -p \
                            option on the command line, mysql prompts for \
                            one.")

        parser.add_argument("-hs", "--host", dest='host',
                            help="Connect to the MySQL server on the \
                            given host.")

        parser.add_argument("-D", "--database", dest='database',
                            help="Database name.")

        parser.add_argument("-P", "--port", dest='port',
                            help="The TCP/IP port number to use for \
                            the connection.")

        parser.add_argument("-cnt", "--connection", dest='connection',
                            help="Select a conection saved in\
                            .connections file")

        args = parser.parse_args()
        self.connect(args)

    def connect(self, args):
        """
        This method is for connect to de database
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
                self.connection = MySQLdb.connect(host=db_host,
                                                  user=args.user,
                                                  passwd=db_pass,
                                                  db=db,
                                                  port=db_port)
                self.cursor = self.connection.cursor()
                self.server_info()
                self.connection_data['host'] = db_host
                self.connection_data['user'] = args.user
                self.connection_data['database'] = db
                self.connection_data['port'] = db_port
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
            db_pass = getpass.getpass()
            config = ConfigParser.ConfigParser()
            config.read(".connections")
            self.connection_data['user'] = config.get(args.connection, "user")
            self.connection_data['host'] = config.get(args.connection, "host")
            self.connection_data['database'] = config.get(args.connection,
                                                          "database")
            self.connection_data['port'] = config.get(args.connection, "port")
            try:
                self.connection_data['port'] = config.get(args.connection,
                                                          'port')
            except:
                pass

            try:
                self.connection = MySQLdb.connect(
                    host=self.connection_data['host'],
                    user=self.connection_data['user'],
                    passwd=db_pass,
                    db=self.connection_data['database'],
                    port=int(self.connection_data['port']))

                self.cursor = self.connection.cursor()
                self.server_info()
                self.prompt = self.get_prompt(self.connection_data['user'],
                                              self.connection_data['host'],
                                              self.connection_data['database'])
                self.get_databases()
                self.get_tables(str(self.connection_data['database']))
                self.get_columns(str(self.connection_data['database']))
                self.get_saved_queries()
            except:
                sys.exit(u"Access denied for user '%s'@'%s'"
                         % (self.connection_data['user'],
                            self.connection_data['host']))
        else:
            sys.exit(u"Please, use -h option to know about how to use TOMy")

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

        if(prompt_config_dict['show_user'] == 'True'):
            if(prompt_config_dict['show_host'] == 'True'):
                prompt = '%s@%s' % (self.connection_data['user'],
                                    self.connection_data['host'])
            else:
                prompt = self.connection_data['user']
        else:
            if(prompt_config_dict['show_host'] == 'True'):
                prompt = self.connection_data['host']
            else:
                prompt = ''

        if(prompt_config_dict['show_db'] == 'True'):
            prompt = '%s\nDB: [%s]' % (prompt,
                                       self.connection_data['database'])

        prompt = prompt + prompt_config_dict['prompt_char'] + ' '

        return prompt

    def server_info(self):
        """
        Shows the server info
        """
        welcome = '.:: Welcome to TOMy!'
        server_info = self.connection.get_server_info()
        print welcome
        print '.:: Server version: %s\n '\
            % (self.colorize(server_info, 'green'))

    def get_databases(self):
        """
        Get the names of the databases in the server.
        """
        query = 'SELECT SCHEMA_NAME FROM information_schema.SCHEMATA'
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        for db in result:
            self.databases.append(db[0])

    def get_tables(self, db):
        """
        Get the tables names
        """
        query = '''SELECT information_schema.TABLES.TABLE_NAME
                   FROM information_schema.TABLES
                   WHERE information_schema.TABLES.TABLE_SCHEMA = "%s"''' % db
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        self.tables = []
        for table in result:
            self.tables.append(table[0])

    def get_columns(self, db):
        """
        Get the fields names
        """
        query = '''SELECT information_schema.COLUMNS.COLUMN_NAME
                   FROM information_schema.COLUMNS
                   WHERE information_schema.COLUMNS.TABLE_SCHEMA = "%s"''' % db
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        self.columns = []
        for column in result:
            self.columns.append(column[0])

    def get_saved_queries(self):
        """
        Get saved queries from saved_queries.txt file
        """
        saved_queries = ConfigParser.ConfigParser()
        saved_queries.read(self.saved_queries_file)
        self.saved_queries = []

        for sq in saved_queries.items('queries'):
            self.saved_queries.append(sq[0])

    def do_DESC(self, stm):
        """
        """
        self.default('DESC %s' % stm)

    do_desc = do_DESC

    def complete_DESC(self, text, line, begidx, endidx):
        if not text:
            completions = self.tables[:]
        else:
            completions = [t for t in self.tables if t.startswith(text)]
        return completions

    complete_desc = complete_DESC

    def do_USE(self, db):
        """
        Change the database:

        USE db_name;
        """
        self.default('USE %s' % db)
        self.connection_data['database'] = db
        self.prompt = self.get_prompt(self.connection_data['user'],
                                      self.connection_data['host'],
                                      self.connection_data['database'])
        self.get_tables(db)
        self.get_columns(db)

    do_use = do_USE

    def complete_USE(self, text, line, begidx, endidx):
        """
        """
        if not text:
            completions = self.databases[:]
        else:
            completions = [d for d in self.databases if d.startswith(text)]
        return completions

    complete_use = complete_USE

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
        # nrows=len(rows) # XXX: Never used
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
