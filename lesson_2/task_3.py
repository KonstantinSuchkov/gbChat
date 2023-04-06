"""
3. Задание на закрепление знаний по модулю yaml. Написать скрипт, автоматизирующий сохранение данных в файле
YAML-формата. Для этого: Подготовить данные для записи в виде словаря, в котором первому ключу соответствует
список, второму — целое число, третьему — вложенный словарь, где значение каждого ключа — это целое число с
юникод-символом, отсутствующим в кодировке ASCII (например, €); Реализовать сохранение данных в файл формата YAML —
например, в файл file.yaml. При этом обеспечить стилизацию файла с помощью параметра default_flow_style,
а также установить возможность работы с юникодом: allow_unicode = True; Реализовать считывание данных из созданного
файла и проверить, совпадают ли они с исходными.
"""

import yaml


dict_to_yaml = {
    'key_list': ['Hotel California', 'Hotel Amelia'],
    'key_int': 2,
    'key_dict': {
        'stars': '1\u2605',
        'price': '1222\u20bd'
    }
}

with open('file.yaml', 'w', encoding="utf-8") as f:
    yaml.dump(dict_to_yaml, f, allow_unicode=True, default_style=False, sort_keys=False)

with open('file.yaml', 'r', encoding="utf-8") as f:
    data_from_yaml = yaml.safe_load(f)

print(dict_to_yaml == data_from_yaml)
