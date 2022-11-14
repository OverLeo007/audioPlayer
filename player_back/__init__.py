"""
Пакет, реализующий основные функции работы плейлиста и взаимодействие с базой данных
"""

from os import listdir

TRACK_PATH = r"C:\Users\sokol\PycharmProjects\audioPlayer\tracks"

list_of_all = [f"{TRACK_PATH}\\{track}" for track in listdir(TRACK_PATH)]
