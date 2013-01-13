#! /usr/bin/python
# -*- coding: utf-8 -*-

import cmd
import sys
import argparse
import MySQLdb
import ConfigParser
import getpass
import TableFormat

class Console(cmd.Cmd):

    prompt = ''
    cursor = ''

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
                connection = MySQLdb.connect(args.host, args.user, args.password, args.database)
                self.cursor = connection.cursor()
                self.prompt = self.get_promt(args.user, args.host, args.database)
            except:
                sys.exit(u"Access denied for user '%s'@'%s'" % (args.user, args.host))

        elif(args.connection is not None):
            pw = getpass.getpass()
            config = ConfigParser.ConfigParser()
            config.read("cmysqlrc")
            db_user = config.get(args.connection, "user")
            db_host = config.get(args.connection, "host")
            db_pass = pw
            try:
                db_database = config.get(args.connection, "database")
                connection = MySQLdb.connect(db_host, db_user, db_pass, db_database)
                self.cursor = connection.cursor()
                self.prompt = self.get_promt(db_user, db_host, db_database)
            except:
                sys.exit(u"Access denied for user '%s'@'%s'" % (db_user, db_host))
        else:
            sys.exit(u"Please, use -h option to know about how to use Copado MySQL Client")

    def get_promt(self, user, host, database = 'None'):
        """
        Get a promt
        """
        promt = user+"@"+host+"\nDB: "+database+" ➜  "
        return promt


    def do_quit (self, s):
        print "Chau vieja!!!"
        return True
    do_exit = do_quit   


    def help_quit (self):
        print "Quits the console"

    def format_output(self, header, result):
        """
        This method formats the query output
        TODO: Make it better ;-)
        """
        columns = len(header)
        rows = len(result)
        output = '|'
        
        # Header format
        for column in header:
            output = output + column[0] + '|'

        output = output + '\n'

        # Result format
        for row in result:
            for c in row:
                output = output + '|' + c

            output = output + '|\n'
                        
        return output


    def default(self, s):
        """ 
        Override the superclass method default to get the imput
        """
        query = s
        self.cursor.execute(query)
        header = self.cursor.description
        result = self.cursor.fetchall()
        
        formated_result = self.format_output(header, result)
        print formated_result

        
    do_EOF = do_quit
    help_EOF = help_quit

if __name__ == "__main__":
    console = Console()
    try:
        console.cmdloop("Salú la barra! Bienvenido a Copado MySQL client\n")
    except KeyboardInterrupt:
        console.do_quit(None)
