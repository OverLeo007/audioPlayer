"""
Соколов Лев Максимович. КИ21-17/1Б.

Модуль, в котором реализован плейлист и сопутствующие ему функции
"""

from typing import Union, Optional

from player_back.double_linked_list import DoubleLinkedList, DoubleLinkedListItem
from player_back.composition import Composition, get_compositions
from player_back.__init__ import list_of_all
from player_back.utils import duration_from_seconds, get_data_path


class PlayListItem(DoubleLinkedListItem):
    """
    Класс элемента плейлиста, для более понятного именного обращения
    """

    def __init__(self, composition: Composition):
        super().__init__(composition)


class PlayList(DoubleLinkedList):
    """
    Класс плейлиста, наследованный от DoubleLinkedList
    Дополнительно реализует методы:
        * next_track
        * previous_track
        * get_dict
    Переопределены следующие методы:
        * __init__
        * swap
        * append
    Свойства (сеттеры и геттеры):
        * current_track
        *
    """

    def __init__(self, head: Union[PlayListItem, None], name: Union[str, None], pic=None) -> None:
        """
        Конструктор плейлиста, вычисляет общее время прослушиваемых треков
        :param head: Голова будущего списка, None, если список пуст
        :param name: Имя списка, будет присвоено 'Unnamed Playlist' если None
        :param pic: Картинка плейлиста, если None и head=None, то возьмет дефолтную картинку из папки data,
        если head is not None то определяет как обложку первой песни
        """
        super().__init__(head)
        if name is None:
            self.name = 'Unnamed Playlist'
        else:
            self.name = name

        self.pic, picpath = None, None

        if pic is not None and head is not None:
            picpath = get_data_path() + f"/{pic}"
        elif pic is None and head is None:
            picpath = get_data_path() + '/img.png'
        elif pic is None and head is not None:
            self.pic = head.data.img
        if self.pic is None:
            with open(picpath, "rb") as file:
                self.pic = file.read()

        if head is None:
            self.duration = '0:0'
        else:
            if hasattr(head.data, "duration"):
                self.duration = duration_from_seconds(sum(map(lambda x: x.data.duration, self)))

        self.__current_track = head

    @property
    def current_track(self) -> Optional[object]:
        """
        Свойство - геттер, возвращает дату текущего трека
        :return: дата текущего трека
        """
        return self.__current_track.data

    @current_track.setter
    def current_track(self, value: Composition) -> None:
        """
        Свойство - сеттер, позволяет установить текущий трек по значению
        :param value: значение, соответствующее одной из нод списка
        """
        self.__current_track = self.find_node(value)

    def next_track(self) -> None:
        """
        Устанавливает в current_track следующий трек
        """
        self.__current_track = self.__current_track.next_item

    def previous_track(self):
        """
        Устанавливает в current_track предыдущий трек
        """
        self.__current_track = self.__current_track.previous_item

    def __str__(self) -> str:
        """
        Строковое представление плейлиста
        :return: строку с именем, кол-вом треков и их общей длительностью
        """
        return f'{self.name} - {self.size} треков, длительностью {self.duration}'

    def get_dict(self) -> dict:
        """
        Возвращает словарь составленный на основе элементов плейлиста
        """
        res = {
            'name': self.name,
            'tracks': []
        }
        for node in self:
            res['tracks'].append(node.data.path)
        return res

    def swap(self, item, direction) -> None:
        """
        Обменивает ноду с предыдущей или следующией, в зависимости от direction
        :param item: значение, соответствующее data одной из нод списка
        :param direction: направление 'up' или 'down'
        """
        first_item = self.find_node(item)
        second_item = first_item.previous_item
        if direction == "down":
            second_item = first_item.next_item
        super().swap(first_item, second_item)

    def append(self, item: Composition) -> None:
        """
        Присоединяет ноду к списку, пересчитывая общую длительность
        :param item: песня, которую добавляем в плейлист
        """
        super().append(item)
        self.duration = duration_from_seconds(sum(map(lambda x: x.data.duration, self)))


def create_node_sequence(data) -> Union[DoubleLinkedListItem, None]:
    """
    Функция создания связанных нод из списка данных
    :param data: список значений для PlaylistItem.data
    :return: головная нода, связанная с остальными
    """
    if not data:
        return None
    head = PlayList.create_node(data[0])
    ptr = head
    for val in data[1:]:
        new_node = PlayList.create_node(val)
        ptr.next_item = new_node
        new_node.previous_item = ptr
        ptr = ptr.next_item

    head.previous_item = ptr
    ptr.next_item = head

    return head


def make_list_of_all() -> PlayList:
    """
    Функция создания плейлиста, состоящего из всех песен в папке tracks
    :return: Playlist со всеми песнями
    """
    return PlayList(create_node_sequence(get_compositions(list_of_all)), "All Tracks")


def make_random_playlist() -> PlayList:
    """
    Функция для создания случайного плейлиста
    :return: случайный Playlist
    """
    from random import shuffle, randint
    from player_back.json_relator import Relator

    tr_list = get_compositions(list_of_all)
    pl_len = randint(2, len(tr_list))
    res = [tr_list.pop(randint(0, len(tr_list) - 1)) for _ in range(pl_len)]
    # res = [tr_list.pop(randint(0, len(tr_list) - 1)) for _ in range(1)]
    shuffle(res)

    rel = Relator(get_data_path() + '/playlists.json')

    return PlayList(create_node_sequence(res), f"random playlist No {len(rel.load())}")


def make_playlist(data: list[Composition], name: str) -> PlayList:
    """
    Функция создания плейлиста из списка композиций
    :param data: список композиций
    :param name: имя плейлиста
    :return: Плейлист с текущими композициями
    """
    seq = create_node_sequence(data)
    return PlayList(seq, name=name)


def make_liked_playlist(data: object) -> PlayList:
    """
    Функция создания плейлиста лайкнутых песен
    :param data: первая песня, в плейлисте
    """
    return PlayList(PlayList.create_node(data), name="♥", pic="liked_playlist_pic.png")


if __name__ == '__main__':
    pl = make_liked_playlist(123)
    print(pl.pic)

    # print(PlayList(PlayList.create_node('213'), 'liked', "liked_playlist_pic.png"))
