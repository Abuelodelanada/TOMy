class Command:

    def install(self, console):
        self.console = console
        command = self.__class__.__name__
        methods = ['do', 'help', 'complete']

        for m in methods:
            # referencia al metodo
            handler = getattr(self, m)
            setattr(console, "%s_%s" %(m, command.lower()), handler)
            setattr(console, "%s_%s" %(m, command.upper()), handler)

    def do(self, stm):
        pass

    def help(self):
        pass

    def complete(self, text, line, begidx, endidx):
        pass

from select import Select
from insert import Insert
from show import Show
from drop import Drop
