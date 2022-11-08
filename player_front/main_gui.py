from sys import argv, exit

from PyQt5.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaContent
from PyQt5.QtWidgets import (QScrollArea, QApplication, QWidget,
                             QMainWindow, QHBoxLayout, QVBoxLayout,
                             QLabel, QSpacerItem, QSizePolicy,
                             QPushButton, QTabWidget, QProgressBar)

from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtCore import Qt, QRect, QUrl
from player_front.ui_templates.templ import Ui_MainWindow

from player_back.playlist import make_random_playlist
from player_back.composition import Composition
from player_back.json_relator import Relator
from player_back.utils import get_data_path

NOW_PLAYING = None


def make_pixmap(img, size_x, size_y):
    pix = QPixmap()
    pix.loadFromData(img)
    pix = pix.scaled(size_x, size_y, Qt.AspectRatioMode.KeepAspectRatio,
                     Qt.TransformationMode.SmoothTransformation)
    return pix


class TrackLayout(QHBoxLayout):
    def __init__(self, composition: Composition):
        super().__init__()

        self.composition = composition

        self.player = QMediaPlayer()
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(composition.path)))

        self.trackPicLabel = QLabel()
        self.trackPicLabel.setPixmap(make_pixmap(composition.img, 50, 50))

        self.trackMetaLabel = QLabel()
        self.trackMetaLabel.setText(str(composition))

        self.spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.playTrackPushButton = QPushButton()
        self.playTrackPushButton.setText("Играть")

        self.stopTrackPushButton = QPushButton()
        self.stopTrackPushButton.setText("Стоп")
        self.stopTrackPushButton.hide()

        self.playTrackPushButton.clicked.connect(self.play)
        self.stopTrackPushButton.clicked.connect(self.stop)

        self.addWidget(self.trackPicLabel)
        self.addWidget(self.trackMetaLabel)
        self.addItem(self.spacerItem)
        self.addWidget(self.playTrackPushButton)
        self.addWidget(self.stopTrackPushButton)

    def play(self):
        self.playTrackPushButton.hide()
        self.stopTrackPushButton.show()
        self.player.play()
        global NOW_PLAYING
        if NOW_PLAYING is not None:
            NOW_PLAYING.stop()
        NOW_PLAYING = self
        print(f"Играем {self.composition.name}")

    def stop(self):
        self.playTrackPushButton.show()
        self.stopTrackPushButton.hide()
        self.player.stop()
        print(f"Перестали играть {self.composition.name}")


class PlayListLayout(QWidget):

    def __init__(self, playlist):
        super().__init__()

        self.layout = QVBoxLayout(self)

        font = QFont()
        font.setFamily("Comic Sans MS")
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(75)

        self.icon = QIcon()
        self.icon.addPixmap(make_pixmap(playlist.pic, 32, 32))

        self.playlist_meta = QLabel()
        self.playlist_meta.setFont(font)
        self.playlist_meta.setText(str(playlist))

        self.trackScrollArea = QScrollArea()
        self.trackScrollArea.setWidgetResizable(True)

        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 780, 540))

        self.tracksLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.tracksLayout.setObjectName("tracksLayout")

        self.trackScrollArea.setWidget(self.scrollAreaWidgetContents)

        self.layout.addWidget(self.playlist_meta)
        self.layout.addWidget(self.trackScrollArea)

        self.name = playlist.name
        self.trackLayouts = []
        for song in playlist:
            self.tracksLayout.addLayout(track := TrackLayout(song.data))
            self.trackLayouts.append(track)
        self.currentTrack = self.trackLayouts[0]

    def to_tab(self):
        return self, self.icon, self.name


class PlayListsTabWidget(QTabWidget):

    def __init__(self, playlists):
        super().__init__()

        self.rel = Relator(get_data_path() + '/playlists.json')
        self.tabs_count = len(playlists)
        self.playlists = playlists

        self.playlistLayouts = []
        for playlist in playlists:
            new_tab = PlayListLayout(playlist)

            self.addTab(*new_tab.to_tab())
            self.playlistLayouts.append(new_tab)

        self.addTab(QWidget(), 'Добавить плейлист')

        self.tabBarClicked.connect(self.if_add_playlist)

    def if_add_playlist(self, index):
        if index == self.tabs_count:
            self.removeTab(index)

            new_playlist = make_random_playlist()
            new_playlist_layout = PlayListLayout(new_playlist)
            self.playlists.append(new_playlist)
            # self.rel.save(self.playlists)

            self.addTab(*new_playlist_layout.to_tab())
            self.playlistLayouts.append(new_playlist_layout)

            self.addTab(QWidget(), 'Добавить плейлист')

            self.tabs_count += 1


class AudioLine(QWidget):
    def __init__(self, playlist):
        super().__init__()
        self.audioLineLayout = QVBoxLayout(self)
        self.trackProgressBar = QProgressBar()
        self.audioLineLayout.addWidget(self.trackProgressBar)

        self.trackProgressBar.setProperty("value", 24)
        self.trackProgressBar.setTextVisible(False)

        self.audioMetaLayout = QHBoxLayout()

        self.addToLikedPushButton = QPushButton("Нравица")
        self.audioMetaLayout.addWidget(self.addToLikedPushButton)

        self.trackMetaLabel = QLabel(str(playlist.currentTrack.composition))
        self.audioMetaLayout.addWidget(self.trackMetaLabel)

        self.playPushButton = QPushButton("Играть")
        self.audioMetaLayout.addWidget(self.playPushButton)

        self.stopPushButton = QPushButton("Стоп")
        self.stopPushButton.hide()
        self.audioMetaLayout.addWidget(self.stopPushButton)

        self.audioLineLayout.addLayout(self.audioMetaLayout)

    def set_track(self, playlist):
        self.trackMetaLabel.setText(str(playlist.currentTrack.composition))


class PlayerUI(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        rel = Relator(get_data_path() + '/playlists.json')

        self.playlists = rel.load_playlists()
        # self.playlists.append(make_random_playlist())
        # rel.save(self.playlists)
        self.tabs = PlayListsTabWidget(self.playlists)

        self.tabs.tabBarClicked.connect(self.change_playlist)

        self.audioline = AudioLine(self.tabs.currentWidget())
        self.audioline.playPushButton.clicked.connect(self.play)

        self.verticalLayout_2.addWidget(self.tabs)
        self.verticalLayout_2.addWidget(self.audioline)

    def play(self):
        print(self.tabs.currentWidget().currentTrack.play())

    def change_playlist(self, index):
        self.audioline.set_track(self.tabs.playlistLayouts[index])


if __name__ == '__main__':
    app = QApplication(argv)
    ex = PlayerUI()
    ex.show()
    app.exec_()
    exit()
