#! /usr/bin/python
# -*- coding: utf-8 -*-

import cmd
import MySQLdb
import ConfigParser

class Console(cmd.Cmd):

    db_user = config.get("mysqlserver", "user")
    db_host = config.get("mysqlserver", "host")
    db_pass = config.get("mysqlserver", "pass")
    db_database = config.get("mysqlserver", "database")
    m = MySQLdb.connect(db_host, db_user, db_pass, db_database)
    cursor = m.cursor()

    prompt = db_user+"@"+db_host+"\nDB: "+db_database+" ➜  "

    def __init__ (self):
        """Constructor"""
        cmd.Cmd.__init__(self)

    def do_quit (self, s):
        print "Chau vieja!!!"
        return True

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
