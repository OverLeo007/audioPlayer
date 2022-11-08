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
    from random import choice, shuffle, randint
    from player_back.json_relator import Relator

    tr_list = get_compositions(list_of_all)
    pl_len = randint(2, len(tr_list))
    res = [tr_list.pop(randint(0, len(tr_list) - 1)) for i in range(pl_len)]
    shuffle(res)

    rel = Relator(get_data_path() + '/playlists.json')

    return PlayList(create_node_sequence(res), f"random playlist No {len(rel.load())}")


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

        if head is None:
            with open(get_data_path() + '/img.png', 'rb') as file:
                self.pic = file.read()
            self.duration = '0:0'
        else:
            self.pic = head.data.img
            self.duration = duration_from_seconds(sum(map(lambda x: x.data.duration, self)))

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


if __name__ == '__main__':
    # pl = make_list_of_all()
    # print(pl.get_dict())
    print(make_random_playlist())
