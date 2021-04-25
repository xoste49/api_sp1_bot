import json
import logging
import os
import sys
import time

import requests
from dotenv import load_dotenv
from telegram import Bot, error

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

time_sleep_error = 10  # Время ожидания после ошибки
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)


class PraktikumException(Exception):
    pass


def timeout_exception():
    """
    Таймаут между после ошибки увеличивающийся в 2 раза после каждой ошибки
    """
    global time_sleep_error
    logging.debug(f'Timeout: {time_sleep_error}с')
    time.sleep(time_sleep_error)
    time_sleep_error *= 2
    if time_sleep_error >= 5120:
        time_sleep_error = 10
        logging.critical(
            'Очень много ошибок или проблемы в работе программы. '
        )


def parse_homework_status(homework):
    """
    Парсим домашнее задание

    :param homework: Задание
    :return: Результат выполнения домашней работы
    """
    logging.debug(f"Парсим домашнее задание: {homework}")
    if 'homework_name' in homework:
        homework_name = homework['homework_name']
        if 'status' in homework:
            homework_status = homework['status']
        else:
            logging.error("Статус домашней работы пуст!")

        statuses = {
            'reviewing': 'Взята в ревью.',
            'approved': 'Ревьюеру всё понравилось, можно приступать к '
                        'следующему уроку.',
            'rejected': 'К сожалению в работе нашлись ошибки.',
        }

        if homework_status in statuses:
            verdict = statuses[homework_status]
        else:
            verdict = statuses[homework_status]
            logging.warning("Обнаружен новый статус, отсутствующий в списке!")

        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    else:
        raise PraktikumException("Задания не обнаружены")


def get_homework_statuses(current_timestamp):
    """
    Получение списка домашних работы от заданного времени.

    :param current_timestamp: Время в формате timestamp
    :return: Статус домашней работы
    """
    logging.debug("Получение списка домашних работы")
    try:
        homework_statuses = requests.get(
            "https://praktikum.yandex.ru/api/user_api/homework_statuses/",
            headers={'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'},
            params={'from_date': current_timestamp}
        )
        homework_statuses_json = homework_statuses.json()
    except requests.exceptions.RequestException as e:
        raise PraktikumException(
            "При обработке вашего запроса возникла неоднозначная "
            f"исключительная ситуация: {e}"
        )
    except json.JSONDecodeError:
        raise PraktikumException(
            "Ответ от сервера должен быть в формате JSON"
        )
    except ValueError as e:
        raise PraktikumException(f"Ошибка в значении {e}")
    except TypeError as e:
        raise PraktikumException(f"Не корректный тип данных {e}")
    except Exception as e:
        raise PraktikumException(e)

    if 'error' in homework_statuses_json:
        if 'error' in homework_statuses_json['error']:
            raise PraktikumException(
                f"{homework_statuses_json['error']['error']}"
            )

    if 'code' in homework_statuses_json:
        raise PraktikumException(
            f"{homework_statuses_json['message']}"
        )

    return homework_statuses_json


def send_message(message, bot_client):
    """
    Отправка сообщения в телеграм

    :param message: Сообщение
    :param bot_client: Экземпляр бота телеграм
    :return: Результат отправки сообщения
    """
    log = message.replace('\n', '')
    logging.info(f"Отправлено сообщение: {log}")
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    logging.debug('Бот запущен! v0.2')
    current_timestamp = int(time.time())  # начальное значение timestamp
    bot = Bot(token=TELEGRAM_TOKEN)

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

        except error.Unauthorized:
            logging.error(
                'Телеграм API: Не авторизован, проверьте TOKEN и CHAT_ID'
            )
            timeout_exception()
        except error.BadRequest as e:
            logging.error(f'Ошибка работы с Телеграм: {e}')
            timeout_exception()
        except error.TelegramError as e:
            logging.error(f'Ошибка работы с Телеграм: {e}')
            timeout_exception()
        except PraktikumException as e:
            logging.error(f'praktikum.yandex.ru: {e}')
            send_message(f'Ошибка: praktikum.yandex.ru: {e}', bot)
            timeout_exception()
        except Exception as e:
            logging.critical(f'Бот столкнулся с ошибкой: {e}')
            timeout_exception()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Выход из программы')
        sys.exit(0)
