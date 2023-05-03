from subprocess import Popen, CREATE_NEW_CONSOLE

p_list = []  # Список клиентских процессов
while True:
    user = input("Запуск 2 тестовых клиентов (t) / Запуск клиентов (add) / Закрыть клиентов (x) / Выйти (q) ")
    if user == 'q':
        break
    elif user == 't':
        # Флаг CREATE_NEW_CONSOLE нужен для ОС Windows,
        # чтобы каждый процесс запускался в отдельном окне консоли
        p_list.append(Popen('python client.py -user Amelia -status 5years', creationflags=CREATE_NEW_CONSOLE))
        p_list.append(Popen('python client.py', creationflags=CREATE_NEW_CONSOLE))
        print(' Запущено 2 клиента')
    # Lesson 9
    # 4. Продолжаем работать над проектом «Мессенджер»: a) Реализовать скрипт, запускающий два клиентских приложения:
    # на чтение чата и на запись в него.Уместно использовать модуль subprocess). b) Реализовать скрипт, запускающий
    # указанное количество клиентских приложений.
    elif user == 'add':
        chaters_number = input('Input number of clients: ')
        if chaters_number.isdigit():
            print('starting')
            for i in range(int(chaters_number)):
                p_list.append(
                    Popen(f'python client.py -user Client{i + 1} -status {i+1}', creationflags=CREATE_NEW_CONSOLE))
        else:
            print('try again')
    elif user == 'x':
        for p in p_list:
            p.kill()
        p_list.clear()

# Message(answer) from server received:  200: 0
# >>>Amelia
# >>>Varvara: Hello
# >>>Varvara: How are you?
# Hi
# >>>Amelia
# I am in kindergarden
# >>>Amelia
