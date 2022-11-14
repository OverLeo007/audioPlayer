"""
Пакет, реализующий основные функции работы плейлиста и взаимодействие с базой данных
"""

from player_back.utils import get_track_path
import os

TRACK_PATH = get_track_path()

list_of_all = [f"{TRACK_PATH}\\{track}" for track in os.listdir(TRACK_PATH)]


if __name__ == '__main__':
    print(list_of_all)