#! /usr/bin/env python
# -*- coding: utf-8 -*-

import cmd
import sys
import argparse
import MySQLdb
import _mysql_exceptions
import ConfigParser
import getpass
import TableFormat

class Console(cmd.Cmd):

    prompt = ''
    cursor = ''
    connection = ''
    connection_data = {'host':'', 'user':'', 'database':''}
    databases = []


    def __init__ (self):
        """Constructor"""
        cmd.Cmd.__init__(self)
        self.arguments()


    def arguments(self):
        """
        Parse arguments
        """
        parser = argparse.ArgumentParser(description='Connect to a MySQL server')
        parser.add_argument("-u", "--user", dest='user', help="The MySQL user name to use when connecting to the server.")
        parser.add_argument("-p", "--password", dest='password', help="The password to use when connecting to the server. If you use the short option form (-p), you cannot have a space between the option and the password. If you omit the password value following the --password or -p option on the command line, mysql prompts for one.")
        parser.add_argument("-hs", "--host", dest='host', help="Connect to the MySQL server on the given host.")
        parser.add_argument("-B", "--database", dest='database', help="Database name.")
        parser.add_argument("-cnt", "--connection", dest='connection', help="Select a conection saved in rc file")

        args = parser.parse_args()
        self.connect(args)


    def connect(self, args):
        """
        This method is for connect to de database
        """

        if(args.host is not None and args.user is not None and args.password is not None and args.database is not None and args.connection is None):
            try:
                self.connection = MySQLdb.connect(args.host, args.user, args.password, args.database)
                self.cursor = self.connection.cursor()
                self.server_info()
                self.connection_data['host'] = args.host
                self.connection_data['user'] = args.user
                self.connection_data['database'] = args.database
                self.prompt = self.get_prompt(self.connection_data['user'], self.connection_data['host'], self.connection_data['database'])
                self.get_databases()
            except:
                sys.exit(u"Access denied for user '%s'@'%s'" % (self.connection_data['user'], self.connection_data['host']))

        elif(args.connection is not None):
            db_pass = getpass.getpass()
            config = ConfigParser.ConfigParser()
            config.read(".connections")
            self.connection_data['user'] = config.get(args.connection, "user")
            self.connection_data['host'] = config.get(args.connection, "host")
            self.connection_data['database'] = config.get(args.connection, "database")
            try:
                self.connection = MySQLdb.connect(self.connection_data['host'], self.connection_data['user'], db_pass, self.connection_data['database'])
                self.cursor = self.connection.cursor()
                self.server_info()
                self.prompt = self.get_prompt(self.connection_data['user'], self.connection_data['host'], self.connection_data['database'])
                self.get_databases()
            except:
                sys.exit(u"Access denied for user '%s'@'%s'" % (self.connection_data['user'], self.connection_data['host']))
        else:
            sys.exit(u"Please, use -h option to know about how to use TOMy")

    def get_prompt(self, user, host, database = 'None'):
        """
        Get a prompt
        """
        # Custom settings if you don't have set up in .config file
        prompt_config_dict = {'show_user':False, 'show_host':False, 'show_db':False, 'prompt_char': '>>>'}

        self.connection_data['host'] = host
        self.connection_data['user'] = user
        self.connection_data['database'] = database

        try:
            prompt_config = ConfigParser.ConfigParser()
            prompt_config.read('.config')
            prompt_config_dict['show_user'] = prompt_config.get('prompt', "show_user")
            prompt_config_dict['show_host'] = prompt_config.get('prompt', "show_host")
            prompt_config_dict['show_db'] = prompt_config.get('prompt', "show_db")
            prompt_config_dict['prompt_char'] = prompt_config.get('prompt', "prompt_char")
        except:
            # TODO: use exceptions in a decent way
            print 'Wrong section definition'


        if(prompt_config_dict['show_user'] == 'True'):
            if(prompt_config_dict['show_host'] == 'True'):
                prompt = self.connection_data['user']+'@'+self.connection_data['host']
            else:
                prompt = self.connection_data['user']
        else:
            if(prompt_config_dict['show_host'] == 'True'):
                prompt = self.connection_data['host']
            else:
                prompt = ''

        if(prompt_config_dict['show_db'] == 'True'):
            prompt = prompt+'\nDB: ['+self.connection_data['database']+'] '

        prompt = prompt+prompt_config_dict['prompt_char']+' '
        return prompt

    def server_info(self):
        """
        Shows the server info
        """
        welcome = 'Welcome to TOMy!'
        server_info = self.connection.get_server_info()
        print welcome
        print 'Server version: '+server_info+'\n'

    def get_databases(self):
        """
        Get the names of the databases in the server.
        """
        query = 'SELECT SCHEMA_NAME FROM information_schema.SCHEMATA'
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        for db in result:
            self.databases.append(db[0])
            
            

    def do_USE(self, db):
        """
        Change the database
        """
        self.default('USE '+db)
        self.connection_data['database'] = db
        self.prompt = self.get_prompt(self.connection_data['user'], self.connection_data['host'], self.connection_data['database'])

    do_use = do_USE


    def complete_USE(self, text, line, begidx, endidx):
        """
        """
        if not text:
            completions = self.databases[:]
        else:
            completions = [ d
                            for d in self.databases
                            if d.startswith(text)
                            ]
        return completions
        
    complete_use = complete_USE

    def do_quit (self, s):
        print "Chau vieja!!!"
        self.connection.close()
        return True
    do_exit = do_quit   


    def help_quit (self):
        print "Quits the console"

    def format_output(self, header, result):
        """
        This method formats the query output
        TODO: Make it better ;-)
        """

        column_names = list()
        rows = list(result)

        for h in header:
            column_names.append(h[0])
    
        print TableFormat.TableFormat(column_names, rows)


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

        except _mysql_exceptions.ProgrammingError, e:
            print 'ERROR ' +str(e[0])+': '+e[1]+'\n'

        
    do_EOF = do_quit
    help_EOF = help_quit

if __name__ == "__main__":
    console = Console()
    try:
        console.cmdloop()
    except KeyboardInterrupt:
        console.do_quit(None)
