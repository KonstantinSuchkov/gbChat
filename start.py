from subprocess import Popen, CREATE_NEW_CONSOLE

p_list = []  # Список клиентских процессов
while True:
    user = input("Запуск тестовых клиентов (t) / Закрыть клиентов (x) / Выйти (q) ")
    if user == 'q':
        break
    elif user == 't':
        # Флаг CREATE_NEW_CONSOLE нужен для ОС Windows,
        # чтобы каждый процесс запускался в отдельном окне консоли
        p_list.append(Popen('python client.py -user Amelia -status 5years', creationflags=CREATE_NEW_CONSOLE))
        p_list.append(Popen('python client.py', creationflags=CREATE_NEW_CONSOLE))
        print(' Запущено 2 клиента')
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