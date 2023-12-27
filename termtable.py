from sty import fg, bg, ef

class TerminalTable:
    def __init__(self, name, header, alignments, sort_by, header_colors, even_colors, odd_colors):
        self.name = name
        self.header = header
        self.alignments = alignments
        self.sort_by = sort_by

        self.header_colors = header_colors
        self.even_colors = even_colors
        self.odd_colors = odd_colors

        self.rows = []
        self.widths = {}
        if 'center' in self.alignments:
            self.padding = 2
        else:
            self.padding = 1

        for section in self.header:
            self.widths[section.lower()] = len(section) + self.padding

    def add_one(self, row):
        for section in self.header:
            if len(row[section.lower()]) + self.padding > self.widths[section.lower()]:
                self.widths[section.lower()] = len(str(row[section.lower()])) + self.padding

        self.rows.append(row)

        if self.sort_by is not None:
            self.rows = sorted(self.rows, key=self.sort_by)

    def add_all(self, rows):
        for row in rows:
            self.add_one(row)

    def __aligned_string_from_section(self, string, section):
        width = self.widths[section.lower()]

        match self.alignments[self.header.index(section)]:
            case 'left':
                return string.ljust(width, ' ')
            case 'center':
                return string.center(width, ' ')
            case _:
                raise ValueError

    def __stringified_header(self):
        stringified_header = ''
        stringified_header += ef.bold + self.header_colors[0] + self.header_colors[1]

        for section in self.header:
            stringified_header += self.__aligned_string_from_section(section, section) 

        stringified_header += ef.rs + bg.rs + fg.rs
        return stringified_header

    def __stringified_row(self, row):
        stringified_row = ''
        stringified_row += self.even_colors[0] + self.even_colors[1]

        for i, section in enumerate(self.header):
            if i % 2 == 0:
                stringified_row += self.even_colors[0] + self.even_colors[1]
            else:
                stringified_row += self.odd_colors[0] + self.odd_colors[1]

            # stringified_row += str(row[section.lower()]).ljust(self.widths[section.lower()], ' ')
            stringified_row += self.__aligned_string_from_section(str(row[section.lower()]), section)
            stringified_row += bg.rs + fg.rs

        return stringified_row

    def __stringified_rows(self):
        return [self.__stringified_row(row) for row in self.rows]

    def __str__(self):
        res = ''
        res += self.__stringified_header() + '\n'
        res += '\n'.join(self.__stringified_rows())

        return res
