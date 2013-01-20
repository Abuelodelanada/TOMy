#! /usr/bin/env python
# -*- coding: utf-8 -*-

import cmd2
import sys
import argparse
import MySQLdb
import _mysql_exceptions
import ConfigParser
import getpass

class Console(cmd2.Cmd):

    prompt = ''
    cursor = ''
    connection = ''
    connection_data = {'host':'', 'user':'', 'database':''}
    databases = []

    def __init__ (self):
        """Constructor"""
        cmd2.Cmd.__init__(self)
        self.arguments()

        # Custom settings if you don't have set up in .config file
        self.color_config_dict = {'borders': 'red', 'border_bold':True, 'result':None, 'result_bold': False}
        self.colors = ('red', 'cyan', 'green', 'magenta', 'blue')
        self.color_config = ConfigParser.ConfigParser()
        self.color_config.read('.config')

        try:
            self.color_config_dict['borders'] = self.color_config.get('colors', "borders")
        except:
            pass

        try:
            self.color_config_dict['borders_bold'] = self.color_config.get('colors', "borders_bold")
        except:
            pass

        try:
            self.color_config_dict['result'] = self.color_config.get('colors', "result")
        except:
            pass

        try:
            self.color_config_dict['result_bold'] = self.color_config.get('colors', "result_bold")
        except:
            pass


    def arguments(self):
        """
        Parse arguments
        """
        parser = argparse.ArgumentParser(description='Connect to a MySQL server')
        parser.add_argument("-u", "--user", dest='user', help="The MySQL user name to use when connecting to the server.")
        parser.add_argument("-p", "--password", dest='password', help="The password to use when connecting to the server. If you use the short option form (-p), you cannot have a space between the option and the password. If you omit the password value following the --password or -p option on the command line, mysql prompts for one.")
        parser.add_argument("-hs", "--host", dest='host', help="Connect to the MySQL server on the given host.")
        parser.add_argument("-B", "--database", dest='database', help="Database name.")
        parser.add_argument("-cnt", "--connection", dest='connection', help="Select a conection saved in .connections file")

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

    def do_DROP(self, db):
        """
        DROP
        """
        self.default('DROP '+db)
        self.prompt = self.get_prompt(self.connection_data['user'], self.connection_data['host'], self.connection_data['database'])
        self.get_databases()

    do_drop = do_DROP


    def complete_DROP(self, text, line, begidx, endidx):
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

    complete_drop = complete_DROP


    def do_SHOW(self, parameter):
        """
        MySQL SHOW command
        """
        self.default('SHOW '+parameter)

    do_show = do_SHOW





    def do_quit (self, s):
        print "Chau vieja!!!"
        self.connection.close()
        return True
    do_exit = do_quit   


    def help_quit (self):
        print "Quits the console"

    def format_output(self, headers_tuple, result):
        """
        This method formats the query output
        Code inspired in http://code.activestate.com/recipes/577202-render-tables-for-text-interface/
        """

        column_names = list()
        rows = list(result)

        for h in headers_tuple:
            column_names.append(h[0])

        headers = column_names
        nrows=len(rows)
        fieldlen=[]

        ncols=len(headers)

        for i in range(ncols):
            max=0
            for j in rows:
                if len(str(j[i]))>max: max=len(str(j[i]))
            fieldlen.append(max)

        for i in range(len(headers)):
            if len(str(headers[i]))>fieldlen[i]: fieldlen[i]=len(str(headers[i]))


        width=sum(fieldlen)+(ncols-1)*3+4

        bar="-"*(width-2)
        bar = "+"+bar+"+"
        pipe = '|'

        if(self.color_config_dict['borders'] in self.colors):
            bar = self.colorize(bar, self.color_config_dict['borders'])
            pipe = self.colorize(pipe, self.color_config_dict['borders'])

        if(self.color_config_dict['borders_bold'] == 'True'):
            bar = self.colorize(bar, 'bold')
            pipe = self.colorize(pipe, 'bold')

        out=[bar]
        header=""
        for i in range(len(headers)):
            header+=pipe+" %s" %self.colorize((str(headers[i])), 'bold') +" "*(fieldlen[i]-len(str(headers[i])))+" "
        header+=pipe
        out.append(header)
        out.append(bar)
        for i in rows:
            line=""
            for j in range(len(i)):
                if(self.color_config_dict['result'] in self.colors):
                    r = self.colorize(str(i[j]), self.color_config_dict['result'])
                else:
                    r = str(i[j])

                if(self.color_config_dict['result_bold'] == 'True'):
                    r = self.colorize(r, 'bold')

                line+= pipe+" %s" %(r) +" "*(fieldlen[j]-len(str(i[j])))+" "

            out.append(line+pipe)

        out.append(bar)
        print "\r\n".join(out)


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

    def cmdloop(self):
        self._cmdloop()


if __name__ == "__main__":
    console = Console()
    try:
        console.cmdloop()
    except KeyboardInterrupt:
        console.do_quit(None)
