"""
Соколов Лев Максимович. КИ21-17/1Б.

Модуль, в котором реализован класс позволяющий сохранять и читать информацию из базы данных
"""

import json
from player_back.playlist import PlayList, make_list_of_all, create_node_sequence
from player_back.composition import get_compositions
from player_back.utils import get_data_path


class Relator:
    """
    Класс взаимодействия с базой данных
    """

    def __init__(self, path: str) -> None:
        """
        Конструктор класса, при инициализации обновляет базу данных,
        с учетом изменений в директории с песнями
        :param path: база данных в виде json файла
        """
        self.json_file = path
        with open(self.json_file, 'r', encoding="utf-8") as file:
            tmp = json.load(file)
            tmp[0] = make_list_of_all().get_dict()
        with open(self.json_file, 'w', encoding="utf-8") as file:
            json.dump(tmp, file, indent=4, ensure_ascii=False)

    def save(self, list_of_playlists: list[PlayList]) -> None:
        """
        Метод сохранения переданных плейлистов в базу данных
        :param list_of_playlists: список плейлистов
        """
        with open(self.json_file, 'w', encoding='utf-8') as file:
            res = []
            for pllst in list_of_playlists:
                res.append(pllst.get_dict())
            json.dump(res, file, indent=4, ensure_ascii=False)

    def load(self) -> list:
        """
        Метод загрузки из базы данных
        :return: возвращает список с json представлениями плейлистов
        """
        with open(self.json_file, 'r', encoding='utf-8') as file:
            return json.load(file)

    def load_playlists(self) -> list:
        """
        Метод возвращающий плейлисты, сохраненные в базе данных
        :return: список из плейлистов
        """
        list_of_playlists = self.load()
        res = []
        for playlist_data in list_of_playlists:
            res.append(PlayList(name=playlist_data['name'],
                                head=create_node_sequence(
                                    get_compositions(playlist_data['tracks']))))
        return res


if __name__ == '__main__':
    rel = Relator(get_data_path() + '/playlists.json')
    # rel.save([make_list_of_all(), PlayList(head=None, name=None)])

    # print(rel.load_playlists())
