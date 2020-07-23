import csv
import unidecode
import hashlib
import statistics
import random
from itertools import cycle

MAX_PER_WEEK = 48
WEEKS = 11


def name_to_hash(name):
    return hashlib.md5(name.encode('utf-8')).hexdigest()


def assisted_days(students: dict) -> list:
    return [students[hash_key]['assisted'] for hash_key in students.keys()]


def parsed_students(filename: str) -> (dict, dict):
    students = {}
    groups = {}
    with open(filename, newline='') as csv_file:
        spam_reader = csv.reader(csv_file, delimiter=',')
        for row in spam_reader:
            _, group, name = [unidecode.unidecode(word) for word in row]
            hash_name = name_to_hash(name)
            students[hash_name] = {
                'name': name, 'group': group, 'assisted': 0}
            if group in groups:
                groups[group].append(hash_name)
            else:
                groups[group] = [hash_name]
    for group_name in groups.keys():
        groups[group_name]

    return (students, groups)


def select_students(group_length, *args: int) -> int:
    return min([random.randint(0, MAX_PER_WEEK - sum(args)), group_length])


def get_n_students(group: list, exclude, number):
    pool = cycle(group)
    students = []
    for i in range(exclude):
        next(pool)
    for i in range(number):
        students.append(next(pool))
    return students


def get_students_per_group(groups: dict) -> (dict, dict):
    first_group = {'A': select_students(len(groups['A']))}
    first_group['C'] = select_students(len(groups['C']), first_group['A'])
    first_group['E'] = select_students(
        len(groups['E']), first_group['A'], first_group['C'])
    first_group['G'] = MAX_PER_WEEK - \
        sum([first_group['A'], first_group['C'], first_group['E']])

    second_group = {'G': len(groups['G']) - first_group['G']}
    second_group['B'] = select_students(len(groups['B']), second_group['G'])
    second_group['D'] = select_students(
        len(groups['D']), second_group['G'], second_group['B'])
    second_group['F'] = MAX_PER_WEEK - \
        sum([second_group['G'], second_group['B'], second_group['D']])

    return first_group, second_group


def simulate(students: dict, groups: dict) -> dict:
    first_group, second_group = get_students_per_group(groups)

    for i in range(WEEKS):
        for group_name in first_group.keys():
            group = groups[group_name]
            take = first_group[group_name]
            exclude = take * i
            for hash in get_n_students(group, exclude, take):
                students[hash]['assisted'] += 1
        for group_name in second_group.keys():
            group = groups[group_name]
            take = second_group[group_name]
            exclude = take * i
            for hash in get_n_students(group, exclude, take):
                students[hash]['assisted'] += 1
    for student in students.values():
        print(student)
    return statistics.stdev([students[hash]['assisted'] for hash in students.keys()])


def main():
    students, groups = parsed_students('alumnos.csv')
    # initial population
    print(simulate(students.copy(), groups.copy()))


if __name__ == "__main__":
    main()
