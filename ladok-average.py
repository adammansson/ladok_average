from pypdf import PdfReader
from datetime import date, datetime
from dataclasses import dataclass

import argparse

@dataclass(repr=False)
class Course:
    name: str
    extent: float
    grade: int
    date: date

    def __repr__(self):
        return ' '.join([self.name, str(self.extent) + 'hp', str(self.grade), self.date.strftime('%Y-%m-%d')])

def is_date(s):
    try:
        datetime.strptime(s, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def find_date_index(words):
    for i, element in enumerate(words):
        if is_date(element):
            return i

    return -1

def process_line(line):
    words = line.split(' ')
    date_index = find_date_index(words)
    
    name = ' '.join(words[:(date_index - 2)])

    extent = words[date_index - 2]
    extent = extent.replace(",", ".")
    extent = float(extent[:len(extent) - 2])

    grade = words[date_index - 1]

    if grade == 'G':
        return None

    grade = int(grade)

    date = words[date_index]
    date = datetime.strptime(date, '%Y-%m-%d')

    return Course(
        name,
        extent,
        grade,
        date
    )

def calculate_average(courses):
    extent_sum = sum(list(map(lambda course : course.extent, courses)))
    weight_sum = sum(list(map(lambda course : course.extent * course.grade, courses)))
    return weight_sum / extent_sum

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                    prog='ladok-average',
                    description='What the program does')

    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--filename', default='Intyg.pdf')
    parser.add_argument('--sortby', choices=['name', 'grade', 'date'], default='date')

    args = parser.parse_args()
    verbose = args.verbose
    file_name = args.filename
    sort_by = args.sortby

    reader = PdfReader(file_name)
    page = reader.pages[0]
    text = page.extract_text()

    lines = text.split('\n')

    is_swedish = lines[0].startswith('Resultatintyg')
    if is_swedish:
        startIndex = lines.index('Benämning Omfattning Betyg Datum Not') + 1
        endIndex = lines.index('Summering')
    else:
        startIndex = lines.index('Code Name Scope Grade Date Note') + 1
        endIndex = lines.index('Summation')
    
    courses = lines[startIndex:endIndex]
    courses = list(map(process_line, courses))

    courses = list(filter(lambda course : False if course is None else True, courses))

    sort_by_key = lambda course : course.date
    match sort_by:
        case 'name':
            sort_by_key = lambda course : course.name
        case 'grade':
            sort_by_key = lambda course : -course.grade

    courses = sorted(courses, key = sort_by_key)

    average = calculate_average(courses)
    average = round(average, 5)

    if verbose:
        print(lines[startIndex - 1])
        for course in courses:
            print(course)
        print()

    print('Your average: ' + str(average))
