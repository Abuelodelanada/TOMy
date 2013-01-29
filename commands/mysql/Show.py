#! /usr/bin/env python
# -*- coding: utf-8 -*-

import commands


class Show(commands.Command):
    def do(self, stm):
        self.console.default('SHOW %s' % stm)

    def help(self):
        help = """
        SHOW {BINARY | MASTER} LOGS
        SHOW BINLOG EVENTS
        SHOW CHARACTER SET [LIKE 'pattern']
        SHOW COLLATION [LIKE 'pattern']
        SHOW [FULL] COLUMNS FROM tbl_name [FROM db_name] [LIKE 'pattern']
        SHOW CREATE DATABASE db_name
        SHOW CREATE TABLE tbl_name
        SHOW DATABASES [LIKE 'pattern']
        SHOW ENGINE engine_name {LOGS | STATUS }
        SHOW [STORAGE] ENGINES
        SHOW ERRORS [LIMIT [offset,] row_count]
        SHOW GRANTS FOR user
        SHOW INDEX FROM tbl_name [FROM db_name]
        SHOW INNODB STATUS
        SHOW [BDB] LOGS
        SHOW MASTER STATUS
        SHOW OPEN TABLES
        SHOW PRIVILEGES
        SHOW [FULL] PROCESSLIST
        SHOW SLAVE HOSTS
        SHOW SLAVE STATUS
        SHOW [GLOBAL | SESSION] STATUS [LIKE 'pattern']
        SHOW TABLE STATUS [FROM db_name] [LIKE 'pattern']
        SHOW TABLES [FROM db_name] [LIKE 'pattern']
        SHOW [GLOBAL | SESSION] VARIABLES [LIKE 'pattern']
        SHOW WARNINGS [LIMIT [offset,] row_count]
        """
        print help

    def complete(self, text, line, begidx, endidx):
        candidates = ['BINARY LOGS', 'MASTER LOGS', 'BINLOG EVENTS',
                     'CHARACTER SET', 'COLLATION', 'COLUMNS FROM tbl_name',
                     'CREATE DATABASE db_name', 'CREATE TABLE tbl_name',
                     'DATABASES', 'ENGINE engine_name STATUS',
                     'ENGINE engine_name LOGS', 'ENGINES', 'ERRORS',
                     'GRANTS FOR user', 'INDEX FROM tbl_name',
                     'INNODB STATUS', '[BDB] LOGS', 'MASTER STATUS',
                     'OPEN TABLES', 'PRIVILEGES', 'PROCESSLIST',
                     'FULL PROCESSLIST', 'SLAVE HOSTS', 'SLAVE STATUS',
                     'GLOBAL STATUS', 'SESSION STATUS', 'TABLE STATUS',
                     'TABLES', 'GLOBAL VARIABLES', 'SESSION VARIABLES',
                     'WARNINGS']
        completions = [t for t in candidates if t.startswith(text)]
        return completions
