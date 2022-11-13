"""
Соколов Лев Максимович. КИ21-17/1Б.

Модуль, в котором реализован класс композиции.
"""

import io
import logging
from typing import Optional

import eyed3
from eyed3 import AudioFile

from player_back.utils import duration_from_seconds, get_data_path


class Composition:
    """
    Класс композиции

    Методы:
        * __init__
        * loader
        * __repr__

    """

    def __init__(self, path: str) -> None:
        """
        Конструктор класса, создает экземпляр песни,
        содержащий ее метаданные, получая их из пути песни
        :param path: путь к аудиофайлу
        """
        audio = self.loader(path)
        self.path = path
        self.name = audio.tag.title
        self.artist = audio.tag.artist
        self.duration = audio.info.time_secs
        try:
            self.img = audio.tag.images[0].image_data
        except Exception:  # pylint: disable=W0703
            with open(get_data_path() + "\\unknown_img.png", 'rb') as file:
                self.img = file.read()

    @staticmethod
    def loader(path: str) -> Optional[AudioFile]:
        """
        Загрузчик аудиофайла, отключающий ненужные логи
        :param path: путь к файлу
        :return: считаный при помощи eyed3 аудиофайл
        """
        log_stream = io.StringIO()
        logging.basicConfig(stream=log_stream, level=logging.INFO)
        audiofile = eyed3.load(path)
        llog = log_stream.getvalue()
        if llog:
            log_stream.truncate(0)
        return audiofile

    def __repr__(self):
        """
        :return: строковое представление песни
        """
        return f'{self.artist} - {self.name} {duration_from_seconds(self.duration)}'


def get_compositions(paths):
    """
    Функция создания списка объектов композиций из их путей
    :param paths:
    :return:
    """
    return [Composition(t_path) for t_path in paths]
