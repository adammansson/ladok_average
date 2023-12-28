from sty import fg, bg

from ladok_average.termtable import TerminalTable

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
    scope = scope[:len(scope) - 2] # remove "hp"

    return float(scope)

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

def create_stats_table():
    return TerminalTable(
        name='stats',
        header=['Statistic', 'Value'],
        alignments=['left', 'center'],
        sort_by=None,
        header_colors=(bg.blue, fg.white),
        even_colors=(bg.da_grey, fg.white),
        odd_colors=(bg.grey, fg.black),
    )
