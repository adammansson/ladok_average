from pypdf import PdfReader
from argparse import ArgumentParser
from pathlib import Path

import ladok_average.courses as courses
import ladok_average.info as info
import ladok_average.stats as stats

def load_lines(input_name):
    reader = PdfReader(input_name)
    page = reader.pages[0]
    text = page.extract_text()

    return text.split('\n')

def run():
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

    lines_list = load_lines(input_name)
    is_swedish = lines_list[0] == 'ResultatintygUtskriftsdatum'

    courses_list = courses.get_courses(lines_list, is_swedish, include_ug)
    courses_table = courses.create_courses_table(sort_by)
    courses_table.add_all(courses_list)

    info_list = info.get_info(lines_list, is_swedish)
    info_table = info.create_info_table()
    info_table.add_all(info_list)

    stats_list = stats.get_stats(courses_list, verbose, ignore_average)
    stats_table = stats.create_stats_table()
    stats_table.add_all(stats_list)

    if output_name:
        courses.write(output_name, courses)

    if verbose:
        print(info_table)
        print(courses_table)

    print(stats_table)
