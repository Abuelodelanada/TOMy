# A nice code found at http://code.activestate.com/recipes/577202-render-tables-for-text-interface/
class TableFormat:
    def __init__(self, *columns):
        self.columns = columns
        self.length = max(len(col.data) for col in columns)
    def get_row(self, rownum=None):
        for col in self.columns:
            if rownum is None:
                yield col.format % col.name
            else:
                yield col.format % col.data[rownum]
    def get_line(self):
        for col in self.columns:
            yield '-' * (col.width + 2)
    def join_n_wrap(self, char, elements):
        return ' ' + char + char.join(elements) + char
    def get_rows(self):
        yield self.join_n_wrap('+', self.get_line())
        yield self.join_n_wrap('|', self.get_row(None))
        yield self.join_n_wrap('+', self.get_line())
        for rownum in range(0, self.length):
            yield self.join_n_wrap('|', self.get_row(rownum))
        yield self.join_n_wrap('+', self.get_line())
    def __str__(self):
        return '\n'.join(self.get_rows())
    class Column():
        LEFT, RIGHT = '-', ''
        def __init__(self, name, data, align=RIGHT):
            self.data = data
            self.name = name
            self.width = max(len(x) for x in data + [name])
            self.format = ' %%%s%ds ' % (align, self.width)

Column = TableFormat.Column
nums = [ '1', '2', '3', '4' ]
speeds = [ '100', '10000', '1500', '12' ]
desc = [ '', 'label 1', 'none', 'very long description' ]
#print TableFormat(
#    Column('NUM', nums),
#    Column('SPEED', speeds),
#    Column('DESC', desc, align=Column.LEFT))
