from pypdf import PdfReader
from argparse import ArgumentParser
from pathlib import Path

from ladok_average.courses import create_courses_table, get_courses, write_courses
from ladok_average.info import create_info_table, get_info
from ladok_average.stats import create_stats_table, get_stats

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

    lines = load_lines(input_name)
    is_swedish = lines[0] == 'ResultatintygUtskriftsdatum'

    courses = get_courses(lines, is_swedish, include_ug)
    courses_table = create_courses_table(sort_by)
    courses_table.add_all(courses)

    info = get_info(lines, is_swedish)
    info_table = create_info_table()
    info_table.add_all(info)

    stats = get_stats(courses, verbose, ignore_average)
    stats_table = create_stats_table()
    stats_table.add_all(stats)

    if output_name:
        write_courses(output_name, courses)

    if verbose:
        print(info_table)
        print(courses_table)

    print(stats_table)
