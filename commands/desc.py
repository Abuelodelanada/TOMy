#! /usr/bin/env python
# -*- coding: utf-8 -*-

import commands


class Desc(commands.Command):
    def do(self, stm):
        self.console.default('DESC %s' % stm)

    def help(self):
        help = """Change the database:
        USE db_name;"""
        print help

    def complete(self, text, line, begidx, endidx):
        candidates = self.console.tables[:]
        completions = [t for t in candidates if t.startswith(text)]
        return completions