import json
from datetime import datetime
from sty import fg, bg

from ladok_average.termtable import TerminalTable

def is_date(word):
    try:
        datetime.strptime(word, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def find_date_index(words):
    for i, word in enumerate(words):
        if is_date(word):
            return i

    raise ValueError

def course_from_line(line, is_swedish):
    words = line.split(' ')
    date_index = find_date_index(words)
    
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

def get_course_indices(lines, is_swedish):
    if is_swedish:
        return (lines.index('Benämning Omfattning Betyg Datum Not') + 1, lines.index('Summering'))
    else:
        return (lines.index('Code Name Scope Grade Date Note') + 1, lines.index('Summation'))

def get_courses(lines, is_swedish, include_ug):
    courses = []
    courses_start_index, courses_end_index = get_course_indices(lines, is_swedish)
    course_lines = lines[courses_start_index:courses_end_index]

    courses += [course_from_line(line, is_swedish) for line in course_lines]

    if not include_ug:
        courses = [course for course in courses if course['grade'] != 'G']

    return courses

def write_courses(output_name, courses):
    courses = json.dumps(courses, indent=4)
    with open(output_name, 'w') as file:
        file.write(courses)

def get_sorting_key(sort_by):
    match sort_by:
        case 'name':
            return lambda course : course['name']
        case 'grade':
            return lambda course : -int(course['grade'])
        case 'date':
            return lambda course : course['date']
        case _:
            raise ValueError

def create_courses_table(sort_by):
    return TerminalTable(
        name='courses',
        header=['Name', 'Scope', 'Grade', 'Date'],
        alignments=['left', 'center', 'center', 'center'],
        sort_by=get_sorting_key(sort_by),
        header_colors=(bg.da_red, fg.white),
        even_colors=(bg.da_grey, fg.white),
        odd_colors=(bg.grey, fg.black),
    )
