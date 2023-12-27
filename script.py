#!/usr/bin/python3

from argparse import ArgumentParser
from pypdf import PdfReader
from datetime import datetime
from termtable import TerminalTable
from sty import fg, bg

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

def course_from_line(line):
    words = line.split(' ')
    date_index = find_date_index(words)
    
    name = ' '.join(words[:(date_index - 2)])
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

def get_course_indices(lines, is_swedish):
    if is_swedish:
        return (lines.index('Benämning Omfattning Betyg Datum Not') + 1, lines.index('Summering'))
    else:
        return (lines.index('Code Name Scope Grade Date Note') + 1, lines.index('Summation'))

def get_sorting_key(sort_by):
    match sort_by:
        case 'name':
            return lambda course : course['name']
        case 'grade':
            return lambda course : -course['grade']
        case 'date':
            return lambda course : course['date']
        case _:
            raise ValueError

def get_lines(file_name):
    reader = PdfReader(file_name)
    page = reader.pages[0]
    text = page.extract_text()

    return text.split('\n')

def get_courses(lines, include_ug):
    courses = list(map(course_from_line, lines))
    if not include_ug:
        courses = list(filter(lambda course : course['grade'] != 'G', courses))
    return courses

def main():
    parser = ArgumentParser(
        prog='ladok-average',
        description='Calculate your grade average from Ladok.')

    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--filename', default='Intyg.pdf')
    parser.add_argument('--sortby', choices=['name', 'grade', 'date'], default='date')
    parser.add_argument('--includeug', action='store_true')
    parser.add_argument('--ignoreaverage', action='store_true')

    args = parser.parse_args()
    verbose = args.verbose
    file_name = args.filename
    sort_by = args.sortby
    include_ug = args.includeug
    ignore_average = args.ignoreaverage

    lines = get_lines(file_name)
    is_swedish = lines[0].startswith('Resultatintyg')
    courses_start_index, courses_end_index = get_course_indices(lines, is_swedish)
    course_lines = lines[courses_start_index:courses_end_index]
    courses = get_courses(course_lines, include_ug)

    courses_table = TerminalTable(
        name='courses',
        header=['Name', 'Scope', 'Grade', 'Date'],
        alignments=['left', 'center', 'center', 'center'],
        sort_by=get_sorting_key(sort_by),
        header_colors=(bg.da_red, fg.white),
        even_colors=(bg.da_grey, fg.white),
        odd_colors=(bg.grey, fg.black),
    )

    courses_table.add_all(courses)

    stats_table = TerminalTable(
        name='stats',
        header=['Statistic', 'Value'],
        alignments=['left', 'center'],
        sort_by=lambda stat : stat['statistic'],
        header_colors=(bg.blue, fg.white),
        even_colors=(bg.da_grey, fg.white),
        odd_colors=(bg.grey, fg.black),
    )


    extent_sum = sum(list(map(lambda course : scope_from_course(course), courses)))
    weight_sum = sum(list(map(lambda course : scope_from_course(course) * grade_from_course(course), courses)))

    if not ignore_average:
        average = weight_sum / extent_sum
        average = round(average, 5)
        stats_table.add_one({
            'statistic': 'Average grade',
            'value': str(average),
        })

    if verbose:
        verbose_stats = [{
            'statistic': 'Number of courses',
            'value': str(len(courses)),
        }, {
            'statistic': 'Total scope',
            'value': str(extent_sum) + 'hp',
        }]
        stats_table.add_all(verbose_stats)

        print(courses_table)

    print(stats_table)

if __name__ == '__main__':
    main()