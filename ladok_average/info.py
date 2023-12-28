from sty import fg, bg

from ladok_average.termtable import TerminalTable

def get_name_index(lines, is_swedish):
    if is_swedish:
        return lines.index('Namn Personnummer') + 1
    else:
        return lines.index('Name Personal identity number') + 1
 
def get_info(lines, is_swedish):
    info = []
    name_index = get_name_index(lines, is_swedish)
    name_and_identity_number = lines[name_index].split(' ')
    name = ' '.join(name_and_identity_number[:len(name_and_identity_number) - 1])
    identity_number = name_and_identity_number[len(name_and_identity_number) - 1]

    info += [{
        'info': name,
    }, {
        'info': identity_number,
    }]

    return info

def create_info_table():
    return TerminalTable(
        name='info',
        header=['Info'],
        alignments=['left'],
        sort_by=None,
        header_colors=(bg.blue, fg.white),
        even_colors=(bg.da_grey, fg.white),
        odd_colors=(bg.grey, fg.black),
    )
