from player_back.double_linked_list import DoubleLinkedList, DoubleLinkedListItem
from player_back.composition import Composition, get_compositions
from player_back.__init__ import list_of_all
from player_back.utils import duration_from_seconds, get_data_path
from typing import Union


def create_node_sequence(data):
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


def make_list_of_all():
    return PlayList(create_node_sequence(get_compositions(list_of_all)), "All Tracks")


def make_random_playlist():
    from random import shuffle, randint
    from player_back.json_relator import Relator

    tr_list = get_compositions(list_of_all)
    pl_len = randint(2, len(tr_list))
    res = [tr_list.pop(randint(0, len(tr_list) - 1)) for i in range(pl_len)]
    shuffle(res)

    rel = Relator(get_data_path() + '/playlists.json')

    return PlayList(create_node_sequence(res), f"random playlist No {len(rel.load())}")


def make_liked_playlist(data):
    return PlayList(PlayList.create_node(data), name="♥", pic="liked_playlist_pic.png")


class PlayListItem(DoubleLinkedListItem):
    def __init__(self, composition: Composition):
        super().__init__(composition)


class PlayList(DoubleLinkedList):
    def __init__(self, head: Union[PlayListItem, None], name: Union[str, None], pic=None):
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
    def current_track(self):
        return self.__current_track.data

    @current_track.setter
    def current_track(self, value):
        self.__current_track = self.find_node(value)

    def next_track(self):
        self.__current_track = self.__current_track.next_item

    def previous_track(self):
        self.__current_track = self.__current_track.previous_item

    def __str__(self):
        return f'{self.name} - {self.size} треков, длительностью {self.duration}'

    def get_dict(self):
        res = {
            'name': self.name,
            'tracks': []
        }
        for node in self:
            res['tracks'].append(node.data.path)
        return res

    def swap(self, item, direction):
        first_item = self.find_node(item)
        second_item = first_item.previous_item
        if direction == "down":
            second_item = first_item.next_item
        super().swap(first_item, second_item)

    def append(self, item: object) -> None:
        super().append(item)
        self.duration = duration_from_seconds(sum(map(lambda x: x.data.duration, self)))


if __name__ == '__main__':
    pl = make_liked_playlist(123)
    print(pl.pic)

    # print(PlayList(PlayList.create_node('213'), 'liked', "liked_playlist_pic.png"))
