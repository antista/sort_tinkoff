import os
import argparse
import big_file_sorter
import config


def is_big_data(filenames):
    total_size = 0
    for file in filenames:
        total_size += os.path.getsize(file)
        if total_size > config.OPERATIVE_MEMORY_SIZE:
            return True
    return False


def read_files(filenames):
    lines = []
    for file in filenames:
        with open(file, 'r') as f:
            for line in f.readlines():
                lines.append(line.replace('\n', ''))
    return lines


def get_args():
    parser = argparse.ArgumentParser(description='Sort lines in files or from stdin.')
    parser.add_argument('filenames', nargs='*', help='files for sorting')
    return parser.parse_args()


def sort():
    filenames = get_args().filenames
    if filenames and not is_big_data(filenames):
        lines = read_files(filenames)
        lines.sort()
        for line in lines:
            print(line)

    else:
        sorter = big_file_sorter.Big_File_Sorter(filenames)
        sorter.sort()
        sorter.print_res()


if __name__ == '__main__':
    sort()
