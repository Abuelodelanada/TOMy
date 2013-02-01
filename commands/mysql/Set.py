#! /usr/bin/env python
# -*- coding: utf-8 -*-

import commands


class Set(commands.Command):
    def do(self, stm):
        self.console.default('SET %s' % stm)
        ac = self.console.raw_query("SHOW variables LIKE 'autocommit'")
        self.console.connection_data['autocommit'] = ac[0][1]
        self.console.prompt = self.console.get_prompt(
                    self.console.connection_data['user'],
                    self.console.connection_data['host'],
                    self.console.connection_data['database'],
                    self.console.connection_data['autocommit'])

    def help(self):
        help = """
        SET variable_assignment [, variable_assignment] ...

        variable_assignment:
        user_var_name = expr
        | [GLOBAL | SESSION] system_var_name = expr
        | [@@global. | @@session. | @@]system_var_name = expr
        """
        print help
