#! /usr/bin/env python
# -*- coding: utf-8 -*-

import commands
from EngineMySQL import *


class Use(commands.Command):
    def do(self, stm):
        self.console.default('USE %s' % stm)
        self.console.connection_data['database'] = stm
        self.console.prompt = self.console.get_prompt(
            self.console.connection_data['user'],
            self.console.connection_data['host'],
            self.console.connection_data['database'])

        a = EngineMySQL()
        self.console.databases_tree = self.console.build_search_tree(
            EngineMySQL.get_databases(a, self.console.cursor))
        self.console.tables_tree = self.console.build_search_tree(
            EngineMySQL.get_tables(a, self.console.cursor, stm))
        self.console.columns_tree = self.console.build_search_tree(
            EngineMySQL.get_columns(a, self.console.cursor, stm))

    def help(self):
        help = """Change the database:
        USE db_name;"""
        print help

    def complete(self, text, line, begidx, endidx):
        result = self.console.databases_tree.search(text)
        completions = [x[0] for x in result]  # discard payload
        return completions
