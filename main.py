from sys import argv, exit

from PyQt5.QtWidgets import QApplication
from player_front.main_gui import PlayerUI
from player_back.json_relator import Relator


def main():
    rel = Relator('data/playlists.json')
    list_of_playlists = rel.load_playlists()

    app = QApplication(argv)
    ex = PlayerUI()
    ex.show()
    app.exec_()
    exit()


if __name__ == '__main__':
    main()
