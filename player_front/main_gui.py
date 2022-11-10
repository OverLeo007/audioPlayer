from sys import argv, exit

from PyQt5.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaContent
from PyQt5.QtWidgets import (QScrollArea, QApplication, QWidget,
                             QMainWindow, QHBoxLayout, QVBoxLayout,
                             QLabel, QSpacerItem, QSizePolicy,
                             QPushButton, QTabWidget, QProgressBar)

from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtCore import Qt, QRect, QUrl, pyqtSignal
from player_front.ui_templates.templ import Ui_MainWindow

from player_back.playlist import make_random_playlist, make_liked_playlist
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

    playing_status_changed = pyqtSignal(str)

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
        self.playing_status_changed.emit("play")
        self.parent().parent().parent().parent().parent().currentTrack = self

    def stop(self):
        global NOW_PLAYING
        NOW_PLAYING = None
        self.playTrackPushButton.show()
        self.stopTrackPushButton.hide()
        self.player.stop()
        self.playing_status_changed.emit("stop")
        print(f"Перестали играть {self.composition.name}")


class PlayListLayout(QWidget):
    cur_track_changed = pyqtSignal()

    def __init__(self, playlist):
        super().__init__()

        self.playlist = playlist

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
            track = TrackLayout(song.data)
            track.playing_status_changed.connect(self.cur_track_change)
            self.tracksLayout.addLayout(track)
            self.trackLayouts.append(track)
        self.currentTrack = self.trackLayouts[0]

    def cur_track_change(self, status):
        if status == "play":
            self.currentTrack = self.sender()
        elif status == "stop":
            self.currentTrack = self.trackLayouts[0]
        self.cur_track_changed.emit()

    def to_tab(self):
        return self, self.icon, self.name

    def append_song(self, song):
        self.playlist.append(song)
        self.tracksLayout.addLayout(track := TrackLayout(song))
        self.trackLayouts.append(track)


class PlayListsTabWidget(QTabWidget):

    playlist_cur_track_changed = pyqtSignal()

    def __init__(self, playlists):
        super().__init__()

        self.rel = Relator(get_data_path() + '/playlists.json')
        self.tabs_count = len(playlists)
        self.playlists = playlists

        self.playlistLayouts = []
        for playlist in playlists:
            new_tab = PlayListLayout(playlist)
            new_tab.cur_track_changed.connect(self.playlist_cur_track_changed_slot)
            self.addTab(*new_tab.to_tab())
            self.playlistLayouts.append(new_tab)

        self.addTab(QWidget(), 'Добавить плейлист')

        self.tabBarClicked.connect(self.if_add_playlist)

    def playlist_cur_track_changed_slot(self):


    def if_add_playlist(self, index):
        if index == self.tabs_count:
            new_playlist = make_random_playlist()
            self.add_playlist(new_playlist)

    def add_playlist(self, new_playlist):
        new_playlist_layout = PlayListLayout(new_playlist)

        self.removeTab(self.tabs_count)
        self.playlists.append(new_playlist)
        self.playlistLayouts.append(new_playlist_layout)

        self.addTab(*new_playlist_layout.to_tab())
        self.addTab(QWidget(), 'Добавить плейлист')

        self.tabs_count += 1

    def get_playlist(self, name):
        if name not in self:
            raise ValueError(f"no playlists with name: {name}")
        for playlist in self.playlists:
            if playlist.name == name:
                return playlist

    def get_playlist_layout(self, name):
        if name not in self:
            raise ValueError(f"no playlists with name: {name}")
        for playlist_layout in self.playlistLayouts:
            if playlist_layout.name == name:
                return playlist_layout

    def __contains__(self, playlist_name):
        for playlist in self.playlists:
            if playlist.name == playlist_name:
                print(playlist.name, playlist_name)
                return True
        return False


class AudioLine(QWidget):
    def __init__(self, playlist):
        super().__init__()

        self.cur_playlist = playlist

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

    def set_playlist(self, playlist):
        self.cur_playlist = playlist
        self.trackMetaLabel.setText(str(self.cur_playlist.currentTrack.composition))


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
        self.audioline.stopPushButton.clicked.connect(self.stop)
        self.audioline.addToLikedPushButton.clicked.connect(self.like)

        self.verticalLayout_2.addWidget(self.tabs)
        self.verticalLayout_2.addWidget(self.audioline)

    def play(self):
        self.audioline.playPushButton.hide()
        self.audioline.stopPushButton.show()

        print(self.tabs.currentWidget().currentTrack.play())

    def stop(self):
        self.audioline.stopPushButton.hide()
        self.audioline.playPushButton.show()
        print(self.tabs.currentWidget().currentTrack.stop())

    def like(self):
        if "♥" not in self.tabs:
            self.tabs.add_playlist(make_liked_playlist(self.tabs.currentWidget().currentTrack.composition))
        else:
            self.tabs.get_playlist_layout("♥").append_song(self.tabs.currentWidget().currentTrack.composition)

    def change_playlist(self, index):
        self.audioline.set_track(self.tabs.playlistLayouts[index])


if __name__ == '__main__':
    app = QApplication(argv)
    ex = PlayerUI()
    ex.show()
    app.exec_()
    exit()
