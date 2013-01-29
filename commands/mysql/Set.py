#! /usr/bin/env python
# -*- coding: utf-8 -*-

import commands


class Set(commands.Command):
    def do(self, stm):
        self.console.default('SET %s' % stm)

    def help(self):
        help = """
        SET variable_assignment [, variable_assignment] ...

        variable_assignment:
        user_var_name = expr
        | [GLOBAL | SESSION] system_var_name = expr
        | [@@global. | @@session. | @@]system_var_name = expr
        """
        print help
