import os
import sys
import logging.handlers
import logging

sys.path.append('../')
log_path = os.path.join(os.getcwd(), 'log/client.log')
# Определить формат сообщений

# Создать обработчик, который выводит сообщения
hand = logging.StreamHandler(sys.stderr)
hand.setLevel(logging.ERROR)
format = logging.Formatter("%(asctime)s %(levelname)s %(filename)-10s %(message)s")
hand.setFormatter(format)
# Создать обработчик, который выводит сообщения в файл
clientlog_hand = logging.FileHandler(log_path, encoding='utf-8')
clientlog_hand.setFormatter(format)
# Создать регистратор верхнего уровня с именем 'server'
client_log = logging.getLogger('client')
client_log.setLevel(logging.DEBUG)
client_log.addHandler(clientlog_hand)
client_log.addHandler(hand)
