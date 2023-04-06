"""
1. Задание на закрепление знаний по модулю CSV. Написать скрипт, осуществляющий выборку определенных данных из
файлов info_1.txt, info_2.txt, info_3.txt и формирующий новый «отчетный» файл в формате CSV. Для этого: Создать
функцию get_data(), в которой в цикле осуществляется перебор файлов с данными, их открытие и считывание данных. В
этой функции из считанных данных необходимо с помощью регулярных выражений извлечь значения параметров
«Изготовитель системы», «Название ОС», «Код продукта», «Тип системы». Значения каждого параметра поместить в
соответствующий список. Должно получиться четыре списка — например, os_prod_list, os_name_list, os_code_list,
os_type_list. В этой же функции создать главный список для хранения данных отчета — например, main_data — и
поместить в него названия столбцов отчета в виде списка: «Изготовитель системы», «Название ОС», «Код продукта»,
«Тип системы». Значения для этих столбцов также оформить в виде списка и поместить в файл main_data (также для
каждого файла); Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл. В этой функции реализовать
получение данных через вызов функции get_data(), а также сохранение подготовленных данных в соответствующий
CSV-файл; Проверить работу программы через вызов функции write_to_csv().
"""

import os
import csv
import re


def get_data():
    os_prod_list = []  # «Изготовитель системы»
    os_name_list = []  # «Название ОС»
    os_code_list = []  # «Код продукта»
    os_type_list = []  # «Тип системы»

    dir_path = os.fsencode(os.getcwd())
    for filename in os.listdir(path=dir_path):
        if filename.endswith(b'.txt'):
            filename = filename.decode("utf-8")  # получение имени файла
            with open(filename, 'r') as f:
                file_content = f.read()

                if 'Изготовитель системы' in file_content:
                    search_point = re.search('Изготовитель системы:(.*)\n', file_content)
                    os_prod_list.append(search_point.group(1).replace(' ', ''))

                if 'Название ОС' in file_content:
                    search_point = re.search('Название ОС:(.*)\n', file_content)
                    os_name_list.append(search_point.group(1).replace(' ', ''))

                if 'Код продукта' in file_content:
                    search_point = re.search('Код продукта:(.*)\n', file_content)
                    os_code_list.append(search_point.group(1).replace(' ', ''))

                if 'Тип системы' in file_content:
                    search_point = re.search('Тип системы:(.*)\n', file_content)
                    os_type_list.append(search_point.group(1).replace(' ', ''))

    main_data = [list(i) for i in zip([1, 2, 3], os_prod_list, os_name_list, os_code_list, os_type_list)]
    return main_data  # [[1, 'LENOVO', 'MicrosoftWindows7Профессиональная', '00971-OEM-1982661-00231', 'x64-basedPC'],..


def write_to_csv(csv_file):
    cols = ['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']
    rows = get_data()
    with open(csv_file, 'w', encoding='utf-8') as f:
        write = csv.writer(f)
        write.writerow(cols)
        for i in rows:
            write.writerow(i)


write_to_csv('task_1.csv')
