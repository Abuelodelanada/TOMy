#! /usr/bin/python
# -*- coding: utf-8 -*-

import cmd
import sys
import argparse
import MySQLdb
import ConfigParser

class Console(cmd.Cmd):

    prompt = ''

    def __init__ (self):
        """Constructor"""
        cmd.Cmd.__init__(self)
        parser = argparse.ArgumentParser(description='Connect to a MySQL server')
        parser.add_argument("-u", "--user", dest='user', required=True, help="The MySQL user name to use when connecting to the server.")
        parser.add_argument("-p", "--password", dest='password', help="The password to use when connecting to the server. If you use the short option form (-p), you cannot have a space between the option and the password. If you omit the password value following the --password or -p option on the command line, mysql prompts for one.")
        parser.add_argument("-hs", "--host", dest='host', help="Connect to the MySQL server on the given host.")
        parser.add_argument("-B", "--database", dest='database', help="Database name.")

        args = parser.parse_args()
        self.connect(args)


    def connect(self, args):
        """
        This method is for connect to de database
        """

        if(args.host is not None and args.user is not None and args.password is not None and args.database is not None):
            m = MySQLdb.connect(args.host, args.user, args.password, args.database)
            cursor = m.cursor()
            self.prompt = args.user+"@"+args.host+"\nDB: "+args.database+" ➜  "

        else:
            config = ConfigParser.ConfigParser()
            config.read("cmysqlrc")
            db_user = config.get("connection1", "user")
            db_host = config.get("connection1", "host")
            db_pass = config.get("connection1", "pass")
            db_database = config.get("connection1", "database")
            m = MySQLdb.connect(db_host, db_user, db_pass, db_database)
            cursor = m.cursor()
            self.prompt = db_user+"@"+db_host+"\nDB: "+db_database+" ➜  "


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
