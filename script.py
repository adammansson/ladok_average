#!/usr/bin/python3

import argparse
from pypdf import PdfReader
from datetime import date, datetime
from dataclasses import dataclass

DATE_FORMAT = '%Y-%m-%d'

@dataclass()
class Course:
    name: str
    scope: float
    grade: str
    date: date

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
        date
    )

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

def calculate_average(courses):
    extent_sum = sum(list(map(lambda course : course.scope, courses)))
    weight_sum = sum(list(map(lambda course : course.scope * number_from_grade(course.grade), courses)))
    return weight_sum / extent_sum

def get_course_indices(lines):
    is_swedish = lines[0].startswith('Resultatintyg')
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

    return sorted(courses, key = sort_by_key)

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

def print_course(course):
    repr = ' '.join([course.name, str(course.scope) + 'hp', str(course.grade), course.date.strftime(DATE_FORMAT)])
    print(repr)

def print_courses(header, courses):
    print(header)
    for course in courses:
        print_course(course)
    print()
 
def main():
    parser = argparse.ArgumentParser(
                    prog='ladok-average',
                    description='Calculate your grade average from Ladok.')

    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--filename', default='Intyg.pdf')
    parser.add_argument('--sortby', choices=['name', 'grade', 'date'], default='date')
    parser.add_argument('--includeug', action='store_true')

    args = parser.parse_args()
    verbose = args.verbose
    file_name = args.filename
    sort_by = args.sortby
    include_ug = args.includeug

    lines = get_lines(file_name)
    courses_start_index, courses_end_index = get_course_indices(lines)
    courses = lines[courses_start_index:courses_end_index]
    courses = processed_courses(courses, sort_by, include_ug)
   
    average = calculate_average(courses)
    average = round(average, 5)

    if verbose:
        print_courses(lines[courses_start_index - 1], courses)

    print('Your average: ' + str(average))

if __name__ == '__main__':
    main()