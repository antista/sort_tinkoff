import os
import sys
import tempfile
import config


class Big_File_Sorter():
    def __init__(self, filenames):
        self.filenames = filenames
        self.tmp_files_count = 0
        self.tmp_file_names = []
        self.start_dir = os.getcwd()
        self.tmp_dir = tempfile.mkdtemp()
        self.result_file = ''
        self.already_merged = 0

    def sort(self):
        if self.filenames:
            self.process_files()
        elif not sys.stdin.isatty():
            self.process_data(sys.stdin)
        self.merge_tmp_files()
        self.delete_tmp_dir()

    def process_files(self):
        for filename in self.filenames:
            with open(filename, 'r') as file:
                self.process_data(file)

    def process_data(self, data):
        os.chdir(self.tmp_dir)
        current_lines, tmp_text = 0, ''
        for line in data:
            line = line.rstrip().replace('"', '').split('\\n')
            for i in line:
                if current_lines != 0:
                    tmp_text += "\n"
                current_lines += 1
                tmp_text += i

            if current_lines == config.MAX_LINES_COUNT:
                self.process_tmp_file(tmp_text)
                current_lines, tmp_text = 0, ''
        if tmp_text != '':
            self.process_tmp_file(tmp_text)
        os.chdir(self.start_dir)

    def process_tmp_file(self, text):
        with open(str(self.tmp_files_count) + ".txt", 'w') as tmp_file:
            self.tmp_files_count += 1
            self.tmp_file_names.append(tmp_file.name)
            tmp_text = self.sort_text(text)
            tmp_file.write(tmp_text)

    def sort_text(self, text):
        tmp_text = text.split('\n')
        tmp_text.sort()
        return '\n'.join(tmp_text)

    def merge_tmp_files(self):
        if len(self.tmp_file_names) == 1:
            self.result_file = self.tmp_file_names[0]
        else:
            os.chdir(self.tmp_dir)
            while len(self.tmp_file_names) - self.already_merged > 1:
                count_of_merging = min(config.MERGE_FILES_COUNT, len(self.tmp_file_names) - self.already_merged)
                self.merge_part_of_tmp_files(count_of_merging)
            os.chdir(self.start_dir)

    def merge_part_of_tmp_files(self, count):
        result_file = open(str(self.tmp_files_count) + ".txt", 'w')
        self.tmp_file_names.append(result_file.name)
        self.tmp_files_count += 1

        files, strings = [], []
        for i in range(count):
            files.append(list(reversed(open(self.tmp_file_names[self.already_merged + i], 'r').readlines())))
            try:
                current_string = files[i].pop()
                current_string = current_string.replace('\n', '')
                strings.append((current_string, i))
            except:
                strings.append((None, i))
        self.already_merged += count
        first_string = True
        while len(strings) > 0:
            if not first_string:
                result_file.write('\n')
            else:
                first_string = False

            id_smaller_string = self.get_smaller_string_id(strings)
            if id_smaller_string == 'END':
                break

            result_file.write(strings[id_smaller_string][0])
            try:
                next_string = files[id_smaller_string].pop()
                next_string = next_string.replace('\n', '')
                strings[id_smaller_string] = (next_string, id_smaller_string)
            except:
                strings[id_smaller_string] = (None, id_smaller_string)

        self.result_file = result_file.name
        result_file.close()

    def get_smaller_string_id(self, strings):
        tmp_arr = []
        for string in strings:
            if string[0] is None:
                continue
            tmp_arr.append([string[0], string[1]])
        if not tmp_arr:
            return 'END'
        tmp_arr.sort()
        return int(tmp_arr[0][1])

    def delete_tmp_dir(self):
        self.make_result_file()
        for i in self.tmp_file_names:
            path = os.path.join(self.tmp_dir, i)
            os.remove(path)
        os.rmdir(self.tmp_dir)

    def make_result_file(self):
        os.chdir(self.tmp_dir)
        result_file = open(self.result_file, 'r')
        os.chdir(self.start_dir)
        input_file = open(config.RESULT_FILE_NAME, 'w')
        for line in result_file:
            input_file.write(line)
        input_file.close()
        result_file.close()
        self.result_file = config.RESULT_FILE_NAME

    def print_res(self):
        with open(self.result_file, 'r') as file:
            for line in file.readlines():
                print(line.replace('\n', ''))
        os.remove(self.result_file)

