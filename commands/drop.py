import commands


class Drop(commands.Command):
    def do(self, stm):
        self.console.default('DROP %s' % stm)
        self.console.prompt = self.console.get_prompt(self.console.connection_data['user'],
                                      self.console.connection_data['host'],
                                      self.console.connection_data['database'])
        self.console.get_databases()

    def help(self):
        help = """DROP [database] [table] [user]"""
        print help

    def complete(self, text, line, begidx, endidx):
        candidates = self.console.databases[:]
        completions = [t for t in candidates if t.startswith(text)]
        return completions