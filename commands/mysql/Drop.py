#! /usr/bin/env python
# -*- coding: utf-8 -*-

import commands
from EngineMySQL import *


class Drop(commands.Command):
    def do(self, stm):
        self.console.default('DROP %s' % stm)
        arguments = stm.split()
        db = arguments[1]
        if(arguments[0].upper() == 'DATABASE' and
           self.console.connection_data['database'] == db):
            self.console.connection_data['database'] = ''

        self.console.prompt = self.console.get_prompt(
            self.console.connection_data['user'],
            self.console.connection_data['host'],
            self.console.connection_data['database'])

        a = EngineMySQL()
        self.console.databases_tree = self.console.build_search_tree(
                EngineMySQL.get_databases(a, self.console.cursor))

    def help(self):
        help = """DROP [database] [table] [user]"""
        print help

    def complete(self, text, line, begidx, endidx):
        result = self.console.databases_tree.search(text)
        completions = [x[0] for x in result]  # discard payload
        return completions
