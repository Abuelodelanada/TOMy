#! /usr/bin/env python
# -*- coding: utf-8 -*-

import commands


class Delete(commands.Command):

    def do(self, stm):
        self.console.default('DELETE %s' % stm)

    def help(self):
        print """
        Single-table syntax:

        DELETE [LOW_PRIORITY] [QUICK] [IGNORE] FROM tbl_name
            [WHERE where_condition]
            [ORDER BY ...]
            [LIMIT row_count]

         Multiple-table syntax:

        DELETE [LOW_PRIORITY] [QUICK] [IGNORE]
            tbl_name[.*] [, tbl_name[.*]] ...
            FROM table_references
            [WHERE where_condition]

         Or:

        DELETE [LOW_PRIORITY] [QUICK] [IGNORE]
            FROM tbl_name[.*] [, tbl_name[.*]] ...
            USING table_references
            [WHERE where_condition]
                """

    def complete(self, text, line, begidx, endidx):
        candidates = self.console.tables + self.console.columns
        completions = [t for t in candidates if t.startswith(text)]
        return completions
