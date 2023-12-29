from sty import fg, bg

from ladok_average.termtable import TerminalTable

def __get_name_index(lines, is_swedish):
    if is_swedish:
        return lines.index('Namn Personnummer') + 1
    else:
        return lines.index('Name Personal identity number') + 1

def __get_verification_index(lines, is_swedish):
    if is_swedish:
        return lines.index('Totalt varav tillgodoräknat Övrig tillgodoräknad utbildning') + 3
    else:
        return lines.index('Total included credited parts Credited education') + 3
 
def get_info(lines, is_swedish):
    info = []
    name_index = __get_name_index(lines, is_swedish)
    name_and_identity_number = lines[name_index].split(' ')
    name = ' '.join(name_and_identity_number[:-1])
    identity_number = name_and_identity_number[-1]
    verification_index = __get_verification_index(lines, is_swedish)
    verification_code = lines[verification_index].split(' ')[-1]

    info += [{
        'info': 'Name',
        'value': name,
    }, {
        'info': 'Identity number',
        'value': identity_number,
    }, {
        'info': 'Verification code',
        'value': verification_code
    }]

    return info

def create_info_table():
    return TerminalTable(
        name='info',
        header=['Info', 'Value'],
        alignments=['left', 'center'],
        sort_by=None,
        header_colors=(bg.blue, fg.white),
        even_colors=(bg.da_grey, fg.white),
        odd_colors=(bg.grey, fg.black),
    )
