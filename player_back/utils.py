"""
Соколов Лев Максимович. КИ21-17/1Б.

Модуль с некоторыми утилитами
"""

import os


def get_data_path() -> str:
    """
    Функция нахождения папки с датой, поддерживающая запуск из любой папки проекта

    :return: путь до папки с датой
    """
    cur_dir = os.getcwd()
    while True:
        if "data" in os.listdir(cur_dir):
            break
        cur_dir = '\\'.join(cur_dir.split("\\")[:-1])

    return os.path.join(cur_dir, 'data')


def get_track_path() -> str:
    """
    Функция нахождения папки с песнями, поддерживающая запуск из любой папки проекта

    :return: путь дол папки с песнями
    """

    cur_dir = os.getcwd()
    while True:
        if "tracks" in os.listdir(cur_dir):
            break
        cur_dir = '\\'.join(cur_dir.split("\\")[:-1])
    return os.path.join(cur_dir, "tracks")


def duration_from_seconds(seconds: float) -> str:
    """
    Функция перевода секунд в читаемый для человека формат

    :param seconds: кол-во секунд
    :return: строка типа hh:mm:ss
    """
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    if hours != 0:
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    return f"{int(minutes):02}:{int(seconds):02}"


def duration_to_sec(milliseconds: int) -> int:
    """
    Функция перевода миллисекунд в секунды

    :param milliseconds: кол-во мс
    :return: секунды
    """
    return milliseconds // 1000


if __name__ == '__main__':
    print(get_data_path())
