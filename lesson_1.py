import subprocess

# 1. Каждое из слов «разработка», «сокет», «декоратор» представить в строковом формате и проверить тип и содержание
# соответствующих переменных. Затем с помощью онлайн-конвертера преобразовать строковые представление в формат
# Unicode и также проверить тип и содержимое переменных.

print('Task 1')

list_1 = ['разработка', 'сокет', 'декоратор']

for i in range(len(list_1)):
    print(f'{i + 1}. Строка - {list_1[i]}, тип - {type(list_1[i])} ')

for i in range(len(list_1)):
    print(f'{i + 1}. Строка - {list_1[i]}, encode - {list_1[i].encode()}, тип - {type(list_1[i].encode())} ')

# Task 1 1. Строка - разработка, тип - <class 'str'> 2. Строка - сокет, тип - <class 'str'> 3. Строка - декоратор,
# тип - <class 'str'> 1. Строка - разработка, encode -
# b'\xd1\x80\xd0\xb0\xd0\xb7\xd1\x80\xd0\xb0\xd0\xb1\xd0\xbe\xd1\x82\xd0\xba\xd0\xb0', тип - <class 'bytes'> 2.
# Строка - сокет, encode - b'\xd1\x81\xd0\xbe\xd0\xba\xd0\xb5\xd1\x82', тип - <class 'bytes'> 3. Строка - декоратор,
# encode - b'\xd0\xb4\xd0\xb5\xd0\xba\xd0\xbe\xd1\x80\xd0\xb0\xd1\x82\xd0\xbe\xd1\x80', тип - <class 'bytes'>

# 2. Каждое из слов «class», «function», «method» записать в байтовом типе без преобразования в последовательность
# кодов (не используя методы encode и decode) и определить тип, содержимое и длину соответствующих переменных.

print('Task 2')

list_1 = [b'class', b'function', b'method']

for i in range(len(list_1)):
    print(f'{i + 1}. Строка - {list_1[i]}, тип - {type(list_1[i])}, длина - {len(list_1[i])} ')

# Task 2
# 1. Строка - b'class', тип - <class 'bytes'>, длина - 5
# 2. Строка - b'function', тип - <class 'bytes'>, длина - 8
# 3. Строка - b'method', тип - <class 'bytes'>, длина - 6

# 3. Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе.

print('Task 3')

list_1 = ['attribute', 'класс', 'функция', 'type']
for i in range(len(list_1)):
    word_bytes = list_1[i].encode('utf-8')
    if word_bytes:
        print(f'{i + 1}. Строка - {word_bytes}, тип - {type(word_bytes)}, длина - {len(word_bytes)} ')

# Task 3
# 1. Строка - b'attribute', тип - <class 'bytes'>, длина - 9
# 2. Строка - b'\xd0\xba\xd0\xbb\xd0\xb0\xd1\x81\xd1\x81', тип - <class 'bytes'>, длина - 10
# 3. Строка - b'\xd1\x84\xd1\x83\xd0\xbd\xd0\xba\xd1\x86\xd0\xb8\xd1\x8f', тип - <class 'bytes'>, длина - 14
# 4. Строка - b'type', тип - <class 'bytes'>, длина - 4

# Ответ: bytes can only contain ASCII literal characters, кириллицей низзя

# 4. Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового представления в
# байтовое и выполнить обратное преобразование (используя методы encode и decode).

print('Task 4')

list_1 = ['разработка', 'администрирование', 'protocol', 'standard']

for i in range(len(list_1)):
    list_1[i] = list_1[i].encode('utf-8')

print(f'Encode - {list_1}')

for i in range(len(list_1)):
    list_1[i] = list_1[i].decode('utf-8')

print(f'Decode - {list_1}')

# Task 4 Encode - [b'\xd1\x80\xd0\xb0\xd0\xb7\xd1\x80\xd0\xb0\xd0\xb1\xd0\xbe\xd1\x82\xd0\xba\xd0\xb0',
# b'\xd0\xb0\xd0\xb4\xd0\xbc\xd0\xb8\xd0\xbd\xd0\xb8\xd1\x81\xd1\x82\xd1\x80\xd0\xb8\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb0
# \xd0\xbd\xd0\xb8\xd0\xb5', b'protocol', b'standard'] Decode - ['разработка', 'администрирование', 'protocol',
# 'standard']

# 5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com и преобразовать результаты из байтовового в строковый тип на
# кириллице.
print('Task 5')

host = ["yandex.ru", "www.youtube.com"]
for i in range(len(host)):
    ping = subprocess.Popen(
        ["ping", "-n", "4", host[i]],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    for line in ping.stdout:
        print(line.decode('cp866'))  # for Windows

# Task 5
# Обмен пакетами с yandex.ru [77.88.55.60] с 32 байтами данных:
# Ответ от 77.88.55.60: число байт=32 время=18мс TTL=243
# Ответ от 77.88.55.60: число байт=32 время=18мс TTL=243
# Ответ от 77.88.55.60: число байт=32 время=18мс TTL=243
# Ответ от 77.88.55.60: число байт=32 время=19мс TTL=243
# Статистика Ping для 77.88.55.60:
# Пакетов: отправлено = 4, получено = 4, потеряно = 0
# (0% потерь)
# Приблизительное время приема-передачи в мс:
# Минимальное = 18мсек, Максимальное = 19 мсек, Среднее = 18 мсек
#
# Обмен пакетами с wide-youtube.l.google.com [173.194.221.198] с 32 байтами данных:
# Ответ от 173.194.221.198: число байт=32 время=20мс TTL=55
# Ответ от 173.194.221.198: число байт=32 время=21мс TTL=55
# Ответ от 173.194.221.198: число байт=32 время=21мс TTL=55
# Ответ от 173.194.221.198: число байт=32 время=21мс TTL=55
# Статистика Ping для 173.194.221.198:
# Пакетов: отправлено = 4, получено = 4, потеряно = 0
# (0% потерь)
# Приблизительное время приема-передачи в мс:
# Минимальное = 20мсек, Максимальное = 21 мсек, Среднее = 20 мсек
# Process finished with exit code 0

# 6. Создать текстовый файл test_file.txt, заполнить его тремя строками: «сетевое программирование», «сокет»,
# «декоратор». Проверить кодировку файла по умолчанию. Принудительно открыть файл в формате Unicode и вывести его
# содержимое.

print('Task 6')

with open("test_file.txt") as test_file:
    for line in test_file:
        print(f'Строка с кодировкой по умолчанию - {line}', end='')

print('\n')

with open("test_file.txt", encoding='utf-8') as test_file:
    for line in test_file:
        print(f'Строка в формате Unicode - {line}', end='')

# Task 6
# Строка с кодировкой по умолчанию - СЃРµС‚РµРІРѕРµ РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёРµ
# Строка с кодировкой по умолчанию - СЃРѕРєРµС‚
# Строка с кодировкой по умолчанию - РґРµРєРѕСЂР°С‚РѕСЂ
#
# Строка в формате Unicode - сетевое программирование
# Строка в формате Unicode - сокет
# Строка в формате Unicode - декоратор
