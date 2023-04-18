import os
import sys
import logging.handlers
import logging


log_path = os.path.join(os.getcwd(), 'log/server.log')
# Определить формат сообщений

# Создать обработчик, который выводит сообщения
hand = logging.StreamHandler(sys.stderr)
hand.setLevel(logging.ERROR)
format = logging.Formatter("%(asctime)s %(levelname)s %(filename)-10s %(message)s")
hand.setFormatter(format)
# Создать обработчик, который выводит сообщения в файл
serverlog_hand = logging.handlers.TimedRotatingFileHandler(log_path, when='midnight', encoding='utf-8')
serverlog_hand.setFormatter(format)
# Создать регистратор верхнего уровня с именем 'server'
server_log = logging.getLogger('server')
server_log.setLevel(logging.DEBUG)
server_log.addHandler(serverlog_hand)
server_log.addHandler(hand)
