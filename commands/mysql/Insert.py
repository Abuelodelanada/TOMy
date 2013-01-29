#! /usr/bin/env python
# -*- coding: utf-8 -*-

import commands


class Insert(commands.Command):

    def do(self, stm):
        self.console.default('INSERT %s' % stm)

    def help(self):
        print """
        INSERT [LOW_PRIORITY | DELAYED | HIGH_PRIORITY] [IGNORE]
            [INTO] tbl_name [(col_name,...)]
            {VALUES | VALUE} ({expr | DEFAULT},...),(...),...
            [ ON DUPLICATE KEY UPDATE
              col_name=expr
                [, col_name=expr] ... ]

        Or:

        INSERT [LOW_PRIORITY | DELAYED | HIGH_PRIORITY] [IGNORE]
            [INTO] tbl_name
            SET col_name={expr | DEFAULT}, ...
            [ ON DUPLICATE KEY UPDATE
              col_name=expr
                [, col_name=expr] ... ]

        Or:

        INSERT [LOW_PRIORITY | HIGH_PRIORITY] [IGNORE]
            [INTO] tbl_name [(col_name,...)]
            SELECT ...
            [ ON DUPLICATE KEY UPDATE
              col_name=expr
                [, col_name=expr] ... ]
        """

    def complete(self, text, line, begidx, endidx):
        candidates = self.console.tables + self.console.columns
        completions = [t for t in candidates if t.startswith(text)]
        return completions
