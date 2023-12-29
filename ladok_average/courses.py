import json
from datetime import datetime
from sty import fg, bg

from ladok_average.termtable import TerminalTable

def __find_date_index(words):
    for i, word in enumerate(words):
        try:
            datetime.strptime(word, '%Y-%m-%d')
            return i
        except ValueError:
            pass

    raise ValueError

def __course_from_line(line, is_swedish):
    words = line.split(' ')
    date_index = __find_date_index(words)
    
    name = ' '.join(words[:(date_index - 2)])
    if not is_swedish: # remove course code
        if name[6] == ' ':
            name = name[7:]
        else:
            name = name[6:]

    scope = words[date_index - 2]
    scope = scope.replace(',', '.')
    grade = words[date_index - 1]
    date = words[date_index]

    return {
        'name': name,
        'scope': scope,
        'grade': grade,
        'date': date,
    }

def __get_course_indices(lines, is_swedish):
    if is_swedish:
        return (lines.index('Benämning Omfattning Betyg Datum Not') + 1, lines.index('Summering'))
    else:
        return (lines.index('Code Name Scope Grade Date Note') + 1, lines.index('Summation'))

def __get_sorting_key(sort_by):
    match sort_by:
        case 'name':
            return lambda course : course['name']
        case 'grade':
            return lambda course : -int(course['grade'])
        case 'date':
            return lambda course : course['date']
        case _:
            raise ValueError

def get_courses(lines, is_swedish, include_ug):
    courses = []
    courses_start_index, courses_end_index = __get_course_indices(lines, is_swedish)
    course_lines = lines[courses_start_index:courses_end_index]

    courses += [__course_from_line(line, is_swedish) for line in course_lines]

    if not include_ug:
        courses = [course for course in courses if course['grade'] != 'G']

    return courses

def create_courses_table(sort_by):
    return TerminalTable(
        name='courses',
        header=['Name', 'Scope', 'Grade', 'Date'],
        alignments=['left', 'center', 'center', 'center'],
        sort_by=__get_sorting_key(sort_by),
        header_colors=(bg.da_red, fg.white),
        even_colors=(bg.da_grey, fg.white),
        odd_colors=(bg.grey, fg.black),
    )
