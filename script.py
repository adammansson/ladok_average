#!/usr/bin/python3

import json
from argparse import ArgumentParser
from pypdf import PdfReader
from datetime import datetime
from termtable import TerminalTable
from sty import fg, bg
from pathlib import Path

def load_lines(input_name):
    reader = PdfReader(input_name)
    page = reader.pages[0]
    text = page.extract_text()

    return text.split('\n')

def get_course_indices(lines, is_swedish):
    if is_swedish:
        return (lines.index('Benämning Omfattning Betyg Datum Not') + 1, lines.index('Summering'))
    else:
        return (lines.index('Code Name Scope Grade Date Note') + 1, lines.index('Summation'))

def get_name_index(lines, is_swedish):
    if is_swedish:
        return lines.index('Namn Personnummer') + 1
    else:
        return lines.index('Name Personal identity number') + 1
 
def write_courses(output_name, courses):
    courses = json.dumps(courses, indent=4)
    with open(output_name, 'w') as file:
        file.write(courses)

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

def grade_from_course(course):
    grade = course['grade']
    match grade:
        case 'G':
            return 3
        case 'U':
            return 0
        case _ if grade.isdigit():
            return int(grade)
        case _:
            raise ValueError

def scope_from_course(course):
    scope = course['scope']
    scope = scope[:len(scope) - 2]

    return float(scope)

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

def get_courses(lines, is_swedish, include_ug):
    courses = []
    courses_start_index, courses_end_index = get_course_indices(lines, is_swedish)
    course_lines = lines[courses_start_index:courses_end_index]

    courses += [course_from_line(line, is_swedish) for line in course_lines]

    if not include_ug:
        courses = [course for course in courses if course['grade'] != 'G']

    return courses

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

def get_stats(courses, verbose, ignore_average):
    stats = []
    total_scope = sum(list(map(lambda course : scope_from_course(course), courses)))
    total_weight = sum(list(map(lambda course : scope_from_course(course) * grade_from_course(course), courses)))
    average = total_weight / total_scope
    average = round(average, 5)

    if not ignore_average:
        stats += [{
            'statistic': 'Average grade',
            'value': str(average),
        }]

    if verbose:
        stats += [{
            'statistic': 'Number of courses',
            'value': str(len(courses)),
        }, {
            'statistic': 'Total scope',
            'value': str(total_scope) + 'hp',
        }]

    return stats

def main():
    parser = ArgumentParser(
        prog='ladok-average',
        description='Calculate your grade average from Ladok.',
    )

    parser.add_argument('input', nargs='?', type=Path, default=Path('Intyg.pdf'))
    parser.add_argument('-o', '--output', type=Path)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--sortby', choices=['name', 'grade', 'date'], default='date')
    parser.add_argument('--includeug', action='store_true')
    parser.add_argument('--ignoreaverage', action='store_true')

    args = parser.parse_args()
    input_name = args.input
    output_name = args.output
    verbose = args.verbose
    sort_by = args.sortby
    include_ug = args.includeug
    ignore_average = args.ignoreaverage

    if input_name.suffix != '.pdf':
        raise ValueError

    lines = load_lines(input_name)
    is_swedish = lines[0] == 'ResultatintygUtskriftsdatum'

    courses_table = TerminalTable(
        name='courses',
        header=['Name', 'Scope', 'Grade', 'Date'],
        alignments=['left', 'center', 'center', 'center'],
        sort_by=get_sorting_key(sort_by),
        header_colors=(bg.da_red, fg.white),
        even_colors=(bg.da_grey, fg.white),
        odd_colors=(bg.grey, fg.black),
    )
    courses = get_courses(lines, is_swedish, include_ug)
    courses_table.add_all(courses)

    info_table = TerminalTable(
        name='personal_info',
        header=['Info'],
        alignments=['left'],
        sort_by=None,
        header_colors=(bg.blue, fg.white),
        even_colors=(bg.da_grey, fg.white),
        odd_colors=(bg.grey, fg.black),
    )
    info = get_info(lines, is_swedish)
    info_table.add_all(info)

    stats_table = TerminalTable(
        name='stats',
        header=['Statistic', 'Value'],
        alignments=['left', 'center'],
        sort_by=None,
        header_colors=(bg.blue, fg.white),
        even_colors=(bg.da_grey, fg.white),
        odd_colors=(bg.grey, fg.black),
    )
    stats = get_stats(courses, verbose, ignore_average)
    stats_table.add_all(stats)

    if output_name:
        write_courses(output_name, courses)

    if verbose:
        print(info_table)
        print(courses_table)

    print(stats_table)

if __name__ == '__main__':
    main()