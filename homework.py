import os
import time

import requests
import logging
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()


"""
logging.debug('123')  # Когда нужна отладочная информация 
logging.info('Сообщение отправлено')  # Когда нужна дополнительная информация
logging.warning('Большая нагрузка, хелп')  # Когда что-то идёт не так, но работает
logging.error('Бот не смог отправить сообщение')  # Когда что-то сломалось
logging.critical('Всё упало! Зовите админа!1!111')  # Когда всё совсем плохо 
"""

PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# filename='api_sp1_bot.log',
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)


def parse_homework_status(homework):
    homework_name = None
    if True:
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    """
    Получение статуса
    :param current_timestamp:

    :return:

    """
    homework_statuses = requests.get(
        f"https://praktikum.yandex.ru/api/user_api/homework_statuses/?from_date={current_timestamp}", headers={'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    )
    logging.debug(homework_statuses)
    return homework_statuses.json()


def send_message(message, bot_client):
    logging.info(message)
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    # проинициализировать бота здесь
    #current_timestamp = int(time.time())  # начальное значение timestamp
    current_timestamp = 0
    bot = Bot(token=TELEGRAM_TOKEN)  # инициализация бота

    while True:
        #try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[0]), bot)
            current_timestamp = new_homework.get('current_date', current_timestamp)  # обновить timestamp
            time.sleep(300)  # опрашивать раз в пять минут

        #except Exception as e:
            #print(f'Бот столкнулся с ошибкой: {e}')
            #time.sleep(5)


if __name__ == '__main__':
    main()
