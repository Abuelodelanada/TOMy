import commands

class Select(commands.Command):

    def do(self, stm):
        self.console.default('SELECT %s' % stm)

    def help(self):
        print """
        MySQL SELECT statement:

        SELECT
        [ALL | DISTINCT | DISTINCTROW ]
            [HIGH_PRIORITY]
            [STRAIGHT_JOIN]
            [SQL_SMALL_RESULT] [SQL_BIG_RESULT] [SQL_BUFFER_RESULT]
            [SQL_CACHE | SQL_NO_CACHE] [SQL_CALC_FOUND_ROWS]
        select_expr [, select_expr ...]
        [FROM table_references
            [PARTITION partition_list]
        [WHERE where_condition]
        [GROUP BY {col_name | expr | position}
            [ASC | DESC], ... [WITH ROLLUP]]
        [HAVING where_condition]
        [ORDER BY {col_name | expr | position}
            [ASC | DESC], ...]
        [LIMIT {[offset,] row_count | row_count OFFSET offset}]
        [PROCEDURE procedure_name(argument_list)]
        [INTO OUTFILE 'file_name'
            [CHARACTER SET charset_name]
            export_options
          | INTO DUMPFILE 'file_name'
          | INTO var_name [, var_name]]
        [FOR UPDATE | LOCK IN SHARE MODE]]
        """

    def complete(self, text, line, begidx, endidx):
        candidates = self.console.tables + self.console.columns
        completions = [t for t in candidates if t.startswith(text)]
        return completions
