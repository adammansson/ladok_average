#!/usr/bin/python3

from argparse import ArgumentParser
from pypdf import PdfReader
from datetime import date, datetime
from dataclasses import dataclass
from sty import fg, bg, ef, rs

DATE_FORMAT = '%Y-%m-%d'
HEAD_START = ef.u + ef.bold + fg.da_black
HEAD_END = rs.bold_dim + rs.u + fg.rs

@dataclass()
class Course:
    name: str
    scope: float
    grade: str
    date: date

@dataclass()
class Statistic:
    name: str
    value: str

def is_date(word):
    try:
        datetime.strptime(word, DATE_FORMAT)
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
    scope = scope.replace(",", ".")
    scope = float(scope[:len(scope) - 2])

    grade = words[date_index - 1]

    date = words[date_index]
    date = datetime.strptime(date, DATE_FORMAT)

    return Course(
        name,
        scope,
        grade,
        date)

def number_from_grade(grade):
    match grade:
        case 'G':
            return 3
        case 'U':
            return 0
        case _ if grade.isdigit():
            return int(grade)
        case _:
            raise ValueError

def get_course_indices(lines, is_swedish):
    if is_swedish:
        return (lines.index('Benämning Omfattning Betyg Datum Not') + 1, lines.index('Summering'))
    else:
        return (lines.index('Code Name Scope Grade Date Note') + 1, lines.index('Summation'))

def sorted_courses(courses, sort_by):
    match sort_by:
        case 'name':
            sort_by_key = lambda course : course.name
        case 'grade':
            sort_by_key = lambda course : -course.grade
        case 'date':
            sort_by_key = lambda course : course.date
        case _:
            raise ValueError

    return sorted(courses, key=sort_by_key)

def get_lines(file_name):
    reader = PdfReader(file_name)
    page = reader.pages[0]
    text = page.extract_text()

    return text.split('\n')

def processed_courses(courses, sort_by, include_ug):
    courses = list(map(course_from_line, courses))
    if not include_ug:
        courses = list(filter(lambda course : course.grade != 'G', courses))
    return sorted_courses(courses, sort_by)

def print_courses_header(header, name_width, scope_width, grade_width, date_width):
    name = HEAD_START + bg.da_grey + ' ' + header[0].ljust(name_width, ' ') + bg.rs + HEAD_END
    scope = HEAD_START + bg.grey + header[1].center(scope_width, ' ') + bg.rs + HEAD_END
    grade = HEAD_START + bg.da_grey + header[2].center(grade_width, ' ') + bg.rs + HEAD_END
    date = HEAD_START + bg.grey + header[3].center(date_width, ' ') + bg.rs + HEAD_END
    print(name + scope + grade + date)

def print_course(course, name_width, scope_width, grade_width, date_width):
    name = bg.da_grey + ' ' + course.name.ljust(name_width, ' ') + bg.rs
    scope = bg.grey + (str(course.scope) + 'hp').center(scope_width, ' ') + bg.rs
    grade = bg.da_grey + (str(course.grade) + '  ').center(grade_width, ' ') + bg.rs
    date = bg.grey + course.date.strftime(DATE_FORMAT).center(date_width, ' ') + bg.rs
    print(name + scope + grade + date)

def print_courses(header, courses):
    header = header.split(" ")

    name_width = max(list(map(lambda course : len(course.name), courses)))
    name_width = max(name_width, len(header[0])) + 1
    scope_width = max(5, len(header[1])) + 2
    grade_width = max(3, len(header[2])) + 2
    date_width = max(10, len(header[3])) + 2

    print_courses_header(header, name_width, scope_width, grade_width, date_width)
    for course in courses:
        print_course(course, name_width, scope_width, grade_width, date_width)

def print_stats_header(header, name_width, value_width):
    name = HEAD_START + bg.blue + ' ' + header[0].ljust(name_width, ' ') + bg.rs + HEAD_END
    value = HEAD_START + bg.li_blue + header[1].center(value_width, ' ') + bg.rs + HEAD_END
    print(fg.black + name + value + fg.rs)

def print_stat(stat, name_width, value_width):
    name = bg.blue + ' ' + stat.name.ljust(name_width, ' ') + bg.rs
    value = bg.li_blue + stat.value.center(value_width, ' ') + bg.rs
    print(name + value)

def print_stats(header, stats):
    name_width = max(list(map(lambda stat : len(stat.name), stats)))
    name_width = max(name_width, len(header[0])) + 1
    value_width = max(list(map(lambda stat : len(stat.value), stats)))
    value_width = max(value_width, len(header[1])) + 2

    print_stats_header(header, name_width, value_width)
    for stat in stats:
        print_stat(stat, name_width, value_width)

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
    courses = lines[courses_start_index:courses_end_index]
    courses = processed_courses(courses, sort_by, include_ug)

    extent_sum = sum(list(map(lambda course : course.scope, courses)))
    weight_sum = sum(list(map(lambda course : course.scope * number_from_grade(course.grade), courses)))
    average = weight_sum / extent_sum
    average = round(average, 5)

    stats = []
    if verbose:
        print_courses(lines[courses_start_index - 1], courses)
        stats = stats + [Statistic('Number of courses', str(len(courses)))]
        stats = stats + [Statistic('Total scope', str(extent_sum) + 'hp')]

    if not ignore_average:
        stats = stats + [Statistic('Average', str(average))]

    if stats:
        print_stats(['Statistic', 'Value'], stats)

if __name__ == '__main__':
    main()