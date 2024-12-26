# pip install tabulate

import csv
import pickle
import os
from tabulate import *
import datetime


def load_table(*filenames, fmt=None, detect_types=False):
    # Проверка указания файла
    if not filenames:
        raise ValueError("Не указаны файлы для загрузки")

    # Проверка существования файла
    for filename in filenames:
        if not os.path.isfile(filename):
            raise FileNotFoundError("Файла с таким названием не существует")

    # Определение формата по первому файлу, если не задан
    if fmt is None:
        _, ext = os.path.splitext(filenames[0])
        if ext.lower() in ('.csv', '.pkl', '.txt'):
            fmt = ext.lower()
        else:
            raise ValueError("Неизвестный формат файла. Используйте расширения .csv, .pkl или .txt")

    all_data = []
    header = None  # Сохранение заголовока (подразумевается, что заголовок есть в каждой таблице)
    reference_width = None  # Число столбцов в первой таблице

    # Проверка файлов на одинаковость формата
    for filename in filenames:
        _, ext = os.path.splitext(filename)
        if fmt != ext.lower():
            raise ValueError("Все файлы должны быть одного формата")

        # Загрузка данных из файлов
        data = []
        if fmt == '.csv':
            with open(filename, 'r', newline='', encoding='utf-8') as f:
                reader = list(csv.reader(f))
                # data = reader (Если строки в Excel таблице не слепляются в одну ячейку с delimiter=',', а с delimiter=';' слепляются, то использовать эту строчку).
                # Закоментировать цикл ниже (отметил строчки знаком #), если с delimiter=';' строки в Excel таблице слепляются в одну ячейку. В функции save_table заменить значение delimiter на ',' (подписал, где это нужно сделать).
                # data.extend(el.split(';') for el in line for line in reader)
                for line in reader:  #
                    for el in line:  #
                        new_el = el.split(';')  #
                        data.append(new_el)  #
        elif fmt == '.pkl':
            with open(filename, 'rb') as f:
                data = pickle.load(f)
        elif fmt == '.txt':
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            data = [line.strip().split('\t') for line in lines if line.strip()]

        # Проверкамналичия данных в файлах
        if not data:
            raise ValueError(f"Файл {filename} пустой")

        current_header = data[0]  # Заголовок первого файла
        body = data[1:]  # Остальные строки

        # Заполнение списка данными из файлов
        if header is None:
            header = current_header
            reference_width = len(header)
            # Проверка строк в первом файле
            for line in body:
                if len(line) != reference_width:
                    raise ValueError(f"Некорректная структура столбцов в файле {filename}")
            all_data.append(header)
            all_data.extend(body)
        else:
            # Проверка на совпадение заголовков в оставшихся файлах
            if current_header != header:
                raise ValueError(f"Заголовок в файле {filename} не совпадает с заголовками предыдущих файлов")
            # Проверка строк в оставшихся файлах
            for line in body:
                if len(line) != reference_width:
                    raise ValueError(f"Некорректная структура столбцов в файле {filename}")
            all_data.extend(body)

    # Определение типа столбцов по надобности
    if detect_types:
        column_types = detect_column_types(all_data)
        return all_data, column_types

    return all_data


def save_table(data, filename, fmt=None, max_rows=None):
    # Проверка наличия данных
    if not data:
        raise ValueError("Нет данных для сохранения")

    # Проверка указания файла для сохранения
    if not filename or not filename.strip():
        raise ValueError("Не указан файл для сохранения")

    # Проверка формата, если не задан
    if fmt is None:
        _, ext = os.path.splitext(filename)
        if ext.lower() in ('.csv', '.pkl', '.txt'):
            fmt = ext.lower()
        else:
            raise ValueError("Неизвестный формат файла. Используйте расширения .csv, .pkl или .txt")

    # Проверка корректности ввода максимального количества строк в одном файле, если оно задано
    if max_rows is not None and max_rows <= 0:
        raise ValueError(f"Параметр max_rows = {max_rows} может быть только положительным")

    # Запись данных в один файл
    if max_rows is None or max_rows >= len(data):
        if fmt == '.csv':
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f,
                                    delimiter=';')  # Если в Excel таблице строка слепляется в одну ячейку, поменять значение delimiter на ','
                writer.writerows(data)
        elif fmt == '.pkl':
            with open(filename, 'wb') as f:
                pickle.dump(data, f)
        elif fmt == '.txt':
            with open(filename, 'w', encoding='utf-8') as f:
                for line in data:
                    f.write('\t'.join(str(el) for el in line) + '\n')
        return

    # Запись данных в несколько файлов
    base, ext = os.path.splitext(filename)  # Базовое имя файла и его расширение
    header = data[0]  # Заголовоки файлов (подразумевается, что заголовок будет в каждом файле)
    total_rows = (
                len(data) - 1)  # Количество строк без учета заголовка (подразумевается, что в каждом файле количество строк будет = заголовочная строка + max_rows)
    file_count = (total_rows // max_rows) + (1 if total_rows % max_rows else 0)  # Количество файлов на фаходе

    start = 1
    for i in range(1, file_count + 1):
        end = min(start + max_rows, total_rows)
        splited_data = [header]
        if start != end:
            splited_data.extend(data[start:end])
        else:
            splited_data.append(data[start])
        # Создание имени для каждого файла с помощью добавления индекса к названию
        splited_data_filename = f"{base}_{i}{ext}"

        if fmt == '.csv':
            with open(splited_data_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerows(splited_data)
        elif fmt == '.pkl':
            with open(splited_data_filename, 'wb') as f:
                pickle.dump(splited_data, f)
        elif fmt == '.txt':
            with open(splited_data_filename, 'w', encoding='utf-8') as f:
                for line in splited_data:
                    f.write('\t'.join(str(el) for el in line) + '\n')

        start = end


def get_rows_by_number(filename, start, stop=None, copy_table=False):
    # Импорт данных из файла
    data = load_table(filename)

    # Проверка данных
    if len(data) == 1:
        raise ValueError("Таблица содержит только заголовок")

    header = data[0]  # Заголовок
    new_data = [header]  # Добавление заголовка, он не считается строкой данных
    # Проверка корректности "начального" индекса
    if start > len(data) - 1:  # Выситание заголовка
        raise IndexError("Номер 'начальной' сохраняемой строки превышает количество строк в файле")
    if start <= 0:
        raise IndexError("Номер 'начальной' сохраняемой строки может быть только положительным")

    # Проверка корректности "конечного" индекса
    if stop is None or start == stop:
        new_data.append(data[start])
    elif stop > len(data) - 1:  # Выситание заголовка
        raise IndexError("Номер 'последней' сохраняемой строки превышает количество строк в файле")
    elif stop <= 0:
        raise IndexError("Номер 'последней' сохраняемой строки может быть только положительным")
    elif stop < start:
        raise IndexError("Номер 'последней' сохраняемой строки не может превышать номер 'начальной' сохраняемой строки")
    else:
        new_data.extend(data[start:(stop + 1)])

    # Если не нужно создавать новый файл
    if not copy_table:
        save_table(new_data, filename)
        return
    # Если нужно создать новый файл с копией данных
    else:
        base, ext = os.path.splitext(filename)
        copied_filename = f"{base}_copied{ext}"
        save_table(new_data, copied_filename)
        return


def get_rows_by_index(filename, indices, copy_table=False):
    if indices == ():
        raise ValueError("Индексы не введены")

    # Импорт данных из файла
    data = load_table(filename)

    # Проверка данных
    if len(data) == 1:
        raise ValueError("Таблица содержит только заголовок")

    header = data[0]  # Заголовок
    header_with_ID = ['ID']
    header_with_ID.extend(header)  # Создание нового заголовка с индексами строк
    new_data = [header_with_ID]  # Добавление заголовка, он не считается строкой данных

    # Если введён один индекс
    if isinstance(indices, int):
        idx = int(indices)
        # Проверка корректности индексов
        if idx > len(data) - 1:  # Вычитание заголовка
            raise IndexError("Номер строки превышает количество строк в файле")
        elif idx <= 0:
            raise IndexError("Номер строки может быть только положительным")
        else:
            new_line = [idx]
            new_line.extend(data[idx])  # Добавление нужных строк с индексом в первом столбце таблицы
            new_data.append(new_line)
    else:
        for idx in set(indices):
            # Проверка корректности индексов
            if idx > len(data) - 1:  # Выситание заголовка
                raise IndexError("Номер строки превышает количество строк в файле")
            elif idx <= 0:
                raise IndexError("Номер строки может быть только положительным")
            else:
                new_line = [idx]
                new_line.extend(data[idx])  # Добавление нужных строк с индексом в первом столбце таблицы
                new_data.append(new_line)

    # Если не нужно создавать новый файл
    if not copy_table:
        save_table(new_data, filename)
        return
    # Если нужно создать новый файл с копией данных
    else:
        base, ext = os.path.splitext(filename)
        copied_filename = f"{base}_copied{ext}"
        save_table(new_data, copied_filename)
        return


def get_column_types(filename, by_number=True):
    # Импорт данных из файла
    data = load_table(filename)

    # Проверка данных
    if len(data) == 1:
        raise ValueError("Таблица содержит только заголовок")

    header = data[0]  # Заголовок
    column_count = len(header)  # Количество столбцов в файле

    # Первая строка после заголовка
    first_line = data[1]

    # Функция для определения типа одного значения
    def detect_type(value):
        if value in ("True", "False"):
            return "bool"
        try:
            int(value)
            return "int"
        except ValueError:
            pass
        try:
            float(value)
            return "float"
        except ValueError:
            pass
        try:
            datetime.datetime.fromisoformat(value)
            return "datetime"
        except ValueError:
            pass
        return "str"

    # Определение типа для каждого столбца по первой строки
    column_types = {}
    if by_number:
        for col_idx in range(column_count):
            column_types[col_idx + 1] = detect_type(first_line[col_idx])
    else:
        for col_idx in range(column_count):
            column_types[header[col_idx]] = detect_type(first_line[col_idx])

    # Проверка остальных строк на соответствие типу столбца
    for col_idx in range(column_count):
        for line in data[2:]:
            current_type = detect_type(line[col_idx])
            value_type = list(column_types.values())[col_idx]
            if current_type != value_type:
                raise TypeError(f"Разный тип значений в {col_idx}-м столбце")

    return column_types


def set_column_types(filename, types_dict,
                     by_number=True):  # Из задания е очень ясно, что должна делать эта функция, так что реализую её по смыслу программы

    '''
        Функция принимает файл и словарь с типами столбцов.
        Функция возвращает данные из файла со значениями в столбцах, приведёнными к нужным типам из словаря types_dict.
        Если в словаре types_dict не задан тип столбца, то функция оставляет тип столбца по умолчанию (str).
        Параметр by_number даёт вункции понять, каким образом определены столбцы в словаре types_dict.
    '''

    # Импорт данных из файла
    data = load_table(filename)

    # Проверка данных
    if len(data) == 1:
        raise ValueError("Таблица содержит только заголовок")

    # Проверка наличия переданноый значений типов столбцов
    if not types_dict:
        raise ValueError("Значений типов столбцов не введены")

    header = data[0]  # заголовок
    column_count = len(header)  # Количество столбцов в файле

    # Сопоставдение каждого индекса столбца с целевым типом столбца
    col_type_map = {}

    if by_number:
        for col_num, col_type in types_dict.items():
            # Проверка введённого словаря на крректность
            if not isinstance(col_num, int):
                raise ValueError("Словарь введён некорректно")
            real_index = col_num - 1
            # Проверка индексов столбцов на корректность
            if real_index < 0 or real_index >= column_count:
                raise IndexError(f"Столбец с индексом {col_num} некорректен (всего столбцов: {column_count})")
            col_type_map[real_index] = col_type
    else:
        for col_name, col_type in types_dict.items():
            # Проверка введённого словаря на крректность
            if isinstance(col_name, int):
                raise ValueError("Словарь введён некорректно")
            # Провека значений столбцов на корректность
            if col_name not in header:
                raise ValueError(f"В заголовке нет столбца с названием '{col_name}'")
            real_index = header.index(col_name)
            col_type_map[real_index] = col_type

    # Функция приведения значения к нужному типу
    def cast_value(value, to_type):
        if to_type == 'int':
            return int(value)
        elif to_type == 'float':
            return float(value)
        elif to_type == 'bool':
            return str(value).lower() in ('true', '1', 'yes')
        elif to_type == 'datetime':
            return datetime.datetime.fromisoformat(value)
        else:
            return str(value)

    # Присвоение типов значений столбцов
    for line_idx in range(1, len(data)):
        for col_idx in range(column_count):
            # Присвоение нового типа значениям в столбцах
            current_type = col_type_map.get(col_idx, 'str')
            original_value = data[line_idx][col_idx]
            try:
                data[line_idx][col_idx] = cast_value(original_value, current_type)
            except ValueError:
                raise ValueError(
                    f"Не удалось привести значение '{original_value}' в столбце '{header[col_idx]}' к типу {current_type}"
                )

    return data


def get_values(data, column=1):
    # Проверка наличия данных
    if not data:
        raise ValueError("Нет данных")

    # Проверка данных
    if len(data) == 1:
        raise ValueError("Таблица содержит только заголовок")

    header = data[0]  # Заголовок
    column_count = len(header)  # Количество столбцов в файле

    # Определение индекса столбца
    if isinstance(column, int):
        # Проверка корректности индекса введенного столбца
        if column <= 0 or column > column_count:
            raise IndexError(f"Некорректный номер столбца: {column}. Всего столбцов: {column_count}")
        col_idx = column - 1
    else:
        # Проверка корректности названия введенного столбца
        if column not in header:
            raise ValueError(f"В заголовке нет столбца с названием '{column}'")
        col_idx = header.index(column)

    # Предполагается, что таблица уже типизирована (если вызывалась set_column_types),
    values = [line[col_idx] for line in data[1:]]

    return values


def get_value(data, column=1):
    # Проверка наличия данных
    if not data:
        raise ValueError("Нет данных")

    # Проверка данных
    if len(data) == 1:
        raise ValueError("Таблица содержит только заголовок")
    if len(data) > 2:
        raise ValueError("В таблице должна быть одна строка без учёта заголовка")

    header = data[0]  # Заголовок
    column_count = len(header)  # Количество столбцов в файле

    # Определение индекса столбца
    if isinstance(column, int):
        # Проверка корректности индекса введенного столбца
        if column <= 0 or column > column_count:
            raise IndexError(f"Некорректный номер столбца: {column}. Всего столбцов: {column_count}")
        col_idx = column - 1
    else:
        # Проверка корректности названия введенного столбца
        if column not in header:
            raise ValueError(f"В заголовке нет столбца с названием '{column}'")
        col_idx = header.index(column)

    # Предполагается, что таблица уже типизирована (если вызывалась set_column_types),
    value = data[1][col_idx]

    return value


def set_values(data, values, column=1):
    # Проверка наличия данных
    if not data:
        raise ValueError("Нет данных")
    if not values:
        raise ValueError(f"Нет данных о значениях столбца {column}")

    # Проверка данных
    if len(data) == 1:
        raise ValueError("Таблица содержит только заголовок")

    # Проверка корректрости переданных значений в столбце
    if len(data) - 1 != len(values):
        raise ValueError(
            "Количество значений в переданном столбце не совпадает с количеством значений в столбце таблицы")

    header = data[0]  # Заголовок
    column_count = len(header)  # Количество столбцов в файле
    new_data = [header]  # Новый список данных

    # Определение индекса столбца
    if isinstance(column, int):
        # Проверка корректности индекса введенного столбца
        if column <= 0 or column > column_count:
            raise IndexError(f"Некорректный номер столбца: {column}. Всего столбцов: {column_count}")

        col_idx = column - 1
    else:
        # Проверка корректности названия введенного столбца
        if column not in header:
            raise ValueError(f"В заголовке нет столбца с названием '{column}'")
        col_idx = header.index(column)

    # Заполнение нового списка данных
    for line_idx, line in enumerate(data[1:]):
        new_line = []
        for idx, el in enumerate(line):
            if idx == col_idx:
                # Проверка на совпадение типа значения с типом столбца
                if type(el) == type(values[line_idx]):
                    new_line.append(values[line_idx])
                else:
                    raise TypeError(f"Тип значения {values[line_idx]} не совпадает с типом столбца {column}")
            else:
                new_line.append(el)
        new_data.append(new_line)

    return new_data


def set_value(data, value, column=1):
    # Проверка наличия данных
    if not data:
        raise ValueError("Нет данных")
    if not value:
        raise ValueError(f"Нет данный о значении столбца {column}")

    # Проверка данных
    if len(data) == 1:
        raise ValueError("Таблица содержит только заголовок")
    if len(data) > 2:
        raise ValueError("В таблице должна быть одна строка без учёта заголовка")

    header = data[0]  # Заголовок
    column_count = len(header)  # Количество столбцов в файле
    new_data = [header]  # Новый список данных

    # Определение индекса столбца
    if isinstance(column, int):
        # Проверка корректности индекса введенного столбца
        if column <= 0 or column > column_count:
            raise IndexError(f"Некорректный номер столбца: {column}. Всего столбцов: {column_count}")

        col_idx = column - 1
    else:
        # Проверка корректности названия введенного столбца
        if column not in header:
            raise ValueError(f"В заголовке нет столбца с названием '{column}'")
        col_idx = header.index(column)

    # Заполнение нового списка данных
    new_line = []
    for el_idx in range(column_count):
        el = data[1][el_idx]
        if el_idx == col_idx:
            # Проверка на совпадение типа значения с типом столбца
            if type(el) == type(value):
                new_line.append(value)
            else:
                raise TypeError(f"Тип значения {value} не совпадает с типом столбца {column}")
        else:
            new_line.append(el)
    new_data.append(new_line)

    return new_data


def print_table(data):
    # Проверка наличия данных
    if not data:
        raise ValueError("Нет данных")

    # Красивый вывод
    print(tabulate(data[1:], data[0], tablefmt="fancy_grid"))


def concat(data1, data2):
    # Проверка наличия данных data1
    if not data1:
        raise ValueError(f"Нет данных в {data1}")

    # Проверка данных data1
    if len(data1) == 1:
        raise ValueError(f"Таблица {data1} содержит только заголовок")

    # Проверка наличия данных data2
    if not data2:
        raise ValueError(f"Нет данных в {data2}")

    # Проверка данных data2
    if len(data2) == 1:
        raise ValueError(f"Таблица {data2} содержит только заголовок")

    header1 = data1[0]  # Заголовок data1
    header2 = data2[0]  # Заголовок data2
    column_count1 = len(header1)  # Количество столбцов в data1
    column_count2 = len(header2)  # Количество столбцов в data2

    # Проверка совпадения форматов data1 и data2
    if header1 != header2 or column_count1 != column_count2:
        raise ValueError("Разные форматы таблиц")

    # Создание новых данных
    new_data = []
    new_data.extend(data1)
    new_data.extend(data2[1:])

    return new_data


def split(data, line_num):
    # Проверка наличия данных
    if not data:
        raise ValueError("Нет данных")

    # Проверка наличия рвзделительной строки
    if not line_num:
        raise ValueError("Не введено значение разделительной строки")

    # Проверка данных
    if len(data) == 1:
        raise ValueError("Таблица содержит только заголовок")

    # Проверка корректности переданного значения строки
    if line_num >= len(data) - 1 or line_num <= 0:
        raise ValueError("Значение разделительной строки введено некорректно")

    header = data[0]  # Заголовок

    # Новые таблицы
    data1 = [header]
    data2 = [header]
    data1.extend(data[1:(line_num + 1)])
    data2.extend(data[(line_num + 1):])

    return data1, data2


def detect_column_types(data):
    # Проверка наличия данных
    if not data:
        raise ValueError("Нет данных")

    # Проверка данных
    if len(data) == 1:
        raise ValueError("Таблица содержит только заголовок")

    header = data[0]  # Заголовок
    column_count = len(data[0])  # Количество строк
    first_data_line = data[1]  # Первая строка после заголовка

    # Функции для определения типа
    def is_int(value: str) -> bool:
        try:
            int(value)
            return True
        except ValueError:
            return False

    def is_float(value: str) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False

    def is_bool(value: str) -> bool:
        lower_val = value.strip().lower()
        return lower_val in ("true", "false", "0", "1", "да", "нет")

    def is_date(value: str, date_formats=None) -> bool:
        import datetime
        if date_formats is None:
            date_formats = ["%Y-%m-%d", "%d.%m.%Y"]
        for fmt in date_formats:
            try:
                datetime.datetime.strptime(value, fmt)
                return True
            except ValueError:
                continue
        return False

    # Определение типа по первой строке после заголовка
    detected_types = []
    for val in first_data_line:
        if is_int(val):
            detected_types.append("int")
        elif is_float(val):
            detected_types.append("float")
        elif is_bool(val):
            detected_types.append("bool")
        elif is_date(val):
            detected_types.append("date")
        else:
            detected_types.append("str")

    return detected_types

