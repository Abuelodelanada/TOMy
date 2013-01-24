import commands


class Use(commands.Command):
    def do(self, stm):
        self.console.default('USE %s' % stm)
        self.console.connection_data['database'] = stm
        self.console.prompt = self.console.get_prompt(
            self.console.connection_data['user'],
            self.console.connection_data['host'],
            self.console.connection_data['database'])
        self.console.get_tables(stm)
        self.console.get_columns(stm)

    def help(self):
        help = """Change the database:
        USE db_name;"""
        print help

    def complete(self, text, line, begidx, endidx):
        candidates = self.console.databases[:]
        completions = [t for t in candidates if t.startswith(text)]
        return completions