#! /usr/bin/env python
# -*- coding: utf-8 -*-

import commands


class Desc(commands.Command):
    def do(self, stm):
        self.console.default("SELECT column_name,\
                             data_type, column_default\
                             FROM information_schema.columns\
                             WHERE table_name = '%s' \
                             ORDER BY ordinal_position ASC" % stm)

    def help(self):
        help = """Change the database:
        USE db_name;"""
        print help

    def complete(self, text, line, begidx, endidx):
        candidates = self.console.tables[:]
        completions = [t for t in candidates if t.startswith(text)]
        return completions
