import json
from pypdf import PdfReader
from argparse import ArgumentParser
from pathlib import Path

import ladok_average.courses as courses
import ladok_average.info as info
import ladok_average.stats as stats

def load_lines_from_pdf(input_name):
    reader = PdfReader(input_name)
    page = reader.pages[0]
    text = page.extract_text()

    return text.split('\n')

def write_as_json(output_name, courses_list, info_list, stats_list):
    json_obj = {}
    json_obj['info'] = info_list
    json_obj['courses'] = courses_list
    json_obj['stats'] = stats_list

    with open(output_name, 'w') as outfile:
        json.dump(json_obj, outfile, indent=4)

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

    lines_list = load_lines_from_pdf(input_name)
    is_swedish = lines_list[0] == 'ResultatintygUtskriftsdatum'

    courses_list = courses.get_courses(lines_list, is_swedish, include_ug)
    info_list = info.get_info(lines_list, is_swedish)
    stats_list = stats.get_stats(courses_list, verbose, ignore_average)

    courses_table = courses.create_courses_table(sort_by)
    courses_table.add_all(courses_list)

    info_table = info.create_info_table()
    info_table.add_all(info_list)

    stats_table = stats.create_stats_table()
    stats_table.add_all(stats_list)

    if output_name:
        write_as_json(output_name, courses_list, info_list, stats_list)

    if verbose:
        print(info_table)
        print(courses_table)

    print(stats_table)
