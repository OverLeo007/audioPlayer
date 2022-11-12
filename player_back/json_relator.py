import json
from player_back.playlist import PlayList, make_list_of_all, create_node_sequence
from player_back.composition import get_compositions
from player_back.utils import get_data_path


class Relator:

    def __init__(self, path: str) -> None:
        self.json_file = path
        with open(self.json_file, 'r', encoding="utf-8") as file:
            tmp = json.load(file)
            tmp[0] = make_list_of_all().get_dict()
        with open(self.json_file, 'w', encoding="utf-8") as file:
            json.dump(tmp, file, indent=4, ensure_ascii=False)

    def save(self, list_of_playlists: list[PlayList]) -> None:
        with open(self.json_file, 'w', encoding='utf-8') as file:
            res = []
            for pllst in list_of_playlists:
                res.append(pllst.get_dict())
            json.dump(res, file, indent=4, ensure_ascii=False)

    def load(self) -> list:
        with open(self.json_file, 'r', encoding='utf-8') as file:
            return json.load(file)

    def load_playlists(self):
        list_of_playlists = self.load()
        res = []
        for playlist_data in list_of_playlists:
            res.append(PlayList(name=playlist_data['name'],
                                head=create_node_sequence(get_compositions(playlist_data['tracks']))))
        return res


if __name__ == '__main__':
    rel = Relator(get_data_path() + '/playlists.json')
    # rel.save([make_list_of_all(), PlayList(head=None, name=None)])

    # print(rel.load_playlists())
