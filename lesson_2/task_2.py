"""
2. Задание на закрепление знаний по модулю json. Есть файл orders в формате JSON с информацией о заказах. Написать
скрипт, автоматизирующий его заполнение данными. Для этого: Создать функцию write_order_to_json(),
в которую передается 5 параметров — товар (item), количество (quantity), цена (price), покупатель (buyer),
дата (date). Функция должна предусматривать запись данных в виде словаря в файл orders.json. При записи данных
указать величину отступа в 4 пробельных символа; Проверить работу программы через вызов функции
write_order_to_json() с передачей в нее значений каждого параметра.
"""

import json


def write_order_to_json(item, quantity, price, buyer, date):
    order_dict = {'item': item, 'quantity': quantity, 'price': price, 'buyer': buyer, 'date': date}

    with open('orders.json', 'r', encoding='utf-8') as f_r:
        data = json.load(f_r)

    with open('orders.json', 'w', encoding='utf-8') as f_w:
        order = data['orders']
        order.append(order_dict)
        json.dump(data, f_w, indent=4, ensure_ascii=False)


write_order_to_json(item='pizza', quantity=3, price=223, buyer='Amelia', date='05.04.2023')
write_order_to_json(item='кофе раф', quantity=3, price=112, buyer='Amelia', date='05.04.2023')
