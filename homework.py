import logging
import os
import time

import requests
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)


def parse_homework_status(homework):
    """
    Парсим домашнее задание

    :param homework: Задание
    :return: Результат выполнения домашней работы
    """
    homework_name = homework['homework_name']
    """
    - reviewing: работа взята в ревью;
    - approved: ревью успешно пройдено;
    - rejected: в работе есть ошибки, нужно поправить.
    """
    if homework['status'] == "reviewing":
        return f'"{homework_name}" взята в ревью.'
    elif homework['status'] == "rejected":
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = (
            'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
        )
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    """
    Получение списка домашних работы от заданного времени

    :param current_timestamp: Время в формате timestamp
    :return: Статус домашней работы
    """
    homework_statuses = requests.get(
        "https://praktikum.yandex.ru/api/user_api/homework_statuses/",
        headers={'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'},
        params={'from_date': current_timestamp}
    )
    return homework_statuses.json()


def send_message(message, bot_client):
    """
    Отправка сообщения в телеграм

    :param message: Сообщение
    :param bot_client: Экземпляр бота телеграм
    :return: Результат отправки сообщения
    """
    logging.info(f"Отправленное сообщение: {message}")
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    logging.debug('Бот запущен!')
    # проинициализировать бота здесь
    current_timestamp = int(time.time())  # начальное значение timestamp
    bot = Bot(token=TELEGRAM_TOKEN)  # инициализация бота

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0]),
                    bot,
                )
            current_timestamp = new_homework.get(
                'current_date', current_timestamp
            )
            # опрашивать раз в пять минут
            time.sleep(300)

        except Exception as e:
            logging.error(f'Бот столкнулся с ошибкой: {e}')
            send_message(f'Бот столкнулся с ошибкой: {e}', bot)
            time.sleep(5)


if __name__ == '__main__':
    main()
