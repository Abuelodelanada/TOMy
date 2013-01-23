class Command:

    def install(self, console):
        self.console = console
        command = self.__class__.__name__

        methods = ['do', 'help', 'complete']

        for m in methods:
            handler = getattr(self, m) # referencia al metodo
            setattr(console, "%s_%s" %(m, command.lower()), handler)  # minusculas
            setattr(console, "%s_%s" %(m, command.upper()), handler)  # mayusculas (porque no funciona case_insensitive de cmd2)

    def do(self, stm):
        pass

    def help(self):
        pass

    def complete(self, text, line, begidx, endidx):
        pass

from select import Select
from insert import Insert
