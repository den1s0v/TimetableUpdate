import ast

import pytest
import csv
from timetable.filedata import FileData

def load_csv_data(file_path, columns:list, name:int = None, skip_rows:int = 1):
    """
    Функция для загрузки данных из CSV файла.
    Возвращает список кортежей (название теста, входные данные, ожидаемый результат).
    """
    data = []
    name_data = []
    skipped_rows = 0

    print("file is opened")
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if skipped_rows < skip_rows:
                skipped_rows += 1
                continue
            new_row = []
            for col in columns:
                new_row.append(row[col])
            data.append(tuple(new_row))

            if name is not None:
                name_data.append(row[name])

    if name is not None:
        return data, name_data
    else:
        return data

def string_to_array(string):
    try:
        # Используем ast.literal_eval для безопасного преобразования строки в массив
        array = ast.literal_eval(string)
        return [int(val) for val in array]
    except (ValueError, SyntaxError) as e:
        # Обработка ошибок в случае неправильного формата строки
        print("Ошибка преобразования строки в массив:", e)
        return None

class TestGetFileNameFromPath:
    test_data, test_name = load_csv_data('CSVFiles/FileData/test_get_file_name.csv', [1, 2], 0)

    @pytest.mark.parametrize("path, expected_file_name", test_data, ids=test_name)
    def test(self, path, expected_file_name):
        file_name = FileData.get_file_name_from_path(path)
        assert file_name == expected_file_name

class TestGetDegree:
    test_data, test_name = load_csv_data('CSVFiles/FileData/test_get_degree.csv', [1, 2, 3], 0)

    @pytest.mark.parametrize("path, expected_dir, will_null", test_data, ids=test_name)
    def test(self, path, expected_dir, will_null):
        degree_dir = FileData._get_degree(path)
        if will_null == "True":
            assert degree_dir is None
        else:
            assert degree_dir == expected_dir

class TestGetCourse:
    @staticmethod
    def helper():
        test_data, test_name = load_csv_data('CSVFiles/FileData/test_get_course_list.csv', [1, 2], 0)
        new_test_data = []
        for row in test_data:
            new_test_data.append(tuple([row[0], string_to_array(row[1])]))
        return new_test_data, test_name

    test_data, test_name = helper()

    @pytest.mark.parametrize("name, expected_list", test_data, ids=test_name)
    def test(self, name, expected_list):
        actual_list = FileData._get_course_list(name)
        assert actual_list == expected_list

class TestGetCorrectFileName:
    test_data, test_name = load_csv_data('CSVFiles/FileData/test_get_correct_file_name.csv', [1, 2], 0)

    @pytest.mark.parametrize("name, expected_name", test_data, ids=test_name)
    def test(self, name, expected_name):
        file_name = FileData.get_correct_file_name(name)
        assert file_name == expected_name