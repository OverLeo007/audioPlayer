from sys import argv, exit

from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import (QScrollArea, QApplication, QWidget,
                             QMainWindow, QHBoxLayout, QVBoxLayout,
                             QLabel, QSpacerItem, QSizePolicy,
                             QPushButton, QTabWidget, QSlider, QFrame, QGroupBox)

from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtCore import Qt, QRect, QUrl, pyqtSignal, QSize
from player_front.ui_templates.templ import Ui_MainWindow

from player_back.playlist import make_random_playlist, make_liked_playlist, PlayList
from player_back.composition import Composition
from player_back.json_relator import Relator
from player_back.utils import get_data_path, duration_from_seconds, duration_to_sec

slot_logs = False


def make_pixmap(img: bytes, size_x: int, size_y: int) -> QPixmap:
    pix = QPixmap()
    pix.loadFromData(img)
    pix = pix.scaled(size_x, size_y, Qt.AspectRatioMode.KeepAspectRatio,
                     Qt.TransformationMode.SmoothTransformation)
    return pix


class TrackGroupBox(QGroupBox):
    switch_clicked = pyqtSignal(str)
    clicked = pyqtSignal()

    def __init__(self, composition: Composition):
        super().__init__()
        self.trackLayout = QHBoxLayout(self)

        # Объявляем
        self.composition = composition

        self.player = QMediaPlayer()
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(composition.path)))

        self.trackPicLabel = QLabel()
        self.trackPicLabel.setPixmap(make_pixmap(composition.img, 50, 50))

        self.trackMetaLabel = QLabel()
        self.trackMetaLabel.setText(str(composition))

        self.spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.moveArrowsLayout = QVBoxLayout()

        self.upArrowLayout = QHBoxLayout()
        self.upArrowPushButton = QPushButton("▲")
        self.upArrowLayout.addWidget(self.upArrowPushButton)

        self.downArrowLayout = QHBoxLayout()
        self.downArrowPushButton = QPushButton("▼")
        self.downArrowLayout.addWidget(self.downArrowPushButton)

        self.moveArrowsLayout.addLayout(self.upArrowLayout)
        self.moveArrowsLayout.addLayout(self.downArrowLayout)

        # Добавляем
        self.trackLayout.addLayout(self.moveArrowsLayout)
        self.trackLayout.addWidget(self.trackPicLabel)
        self.trackLayout.addWidget(self.trackMetaLabel)
        self.trackLayout.addItem(self.spacerItem)

        # Настраиваем
        self.upArrowPushButton.setMaximumSize(QSize(25, 16777215))
        self.upArrowPushButton.setFlat(True)
        self.upArrowPushButton.clicked.connect(self.move_track_up)

        self.downArrowPushButton.setMaximumSize(QSize(25, 16777215))
        self.downArrowPushButton.setFlat(True)
        self.downArrowPushButton.clicked.connect(self.move_track_down)

    @property
    def name(self):
        return self.composition.name

    @property
    def artist(self):
        return self.composition.artist

    @property
    def duration(self):
        return self.composition.duration

    @property
    def img(self):
        return self.composition.img

    @property
    def path(self):
        return self.composition.path

    def mousePressEvent(self, event) -> None:
        if slot_logs:
            print(f"[TRACK]{self.composition} хочет играть")
        self.clicked.emit()

    def move_track_up(self):
        if slot_logs:
            print(f"[TRACK]{self.composition} хочет поменяться с верхней")
        self.switch_clicked.emit("up")

    def move_track_down(self):
        if slot_logs:
            print(f"[TRACK]{self.composition} хочет поменяться с нижней")
        self.switch_clicked.emit("down")


class PlayListWidget(QWidget):
    list_updated = pyqtSignal()
    want_to_activate = pyqtSignal()

    def __init__(self, playlist: PlayList):
        super().__init__()

        # Объявляем
        self.playlist = playlist
        self.layout = QVBoxLayout(self)
        self.icon = QIcon()
        self.playlist_meta = QLabel()
        self.trackScrollArea = QScrollArea()
        self.scrollAreaWidget = QWidget()
        self.scrollAreaWidgetLayout = QVBoxLayout(self.scrollAreaWidget)
        self.trackScrollArea.setWidget(self.scrollAreaWidget)
        self.activateButton = QPushButton("Активировать плейлист")

        if playlist.name != "All Tracks":
            self.controlButtonsLayout = QHBoxLayout()
            self.editButton = QPushButton("Редактировать плейлист")
            self.editButton.clicked.connect(self.edit_playlist)
            self.deleteButton = QPushButton("Удалить плейлист")
            self.deleteButton.clicked.connect(self.delete_playlist)
            self.controlButtonsLayout.addWidget(self.editButton)
            self.controlButtonsLayout.addWidget(self.deleteButton)
            self.controlButtonsLayout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.trackGroupBoxes = []

        # Добавляем в лейауты
        self.layout.addWidget(self.playlist_meta)
        if playlist.name != "All Tracks":
            self.layout.addLayout(self.controlButtonsLayout)
        self.layout.addWidget(self.activateButton)
        self.layout.addWidget(self.trackScrollArea)

        for song in self.playlist:
            track = TrackGroupBox(song.data)
            track.switch_clicked.connect(self.switch_tracks)
            track.clicked.connect(self.song_picked)
            self.scrollAreaWidgetLayout.addWidget(track)
            self.trackGroupBoxes.append(track)

        # Настраиваем
        font = QFont()
        font.setFamily("Comic Sans MS")
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(75)

        self.playlist_meta.setFont(font)
        self.playlist_meta.setText(str(playlist))

        self.activateButton.clicked.connect(self.activate)

        self.icon.addPixmap(make_pixmap(playlist.pic, 32, 32))

        self.trackScrollArea.setWidgetResizable(True)

        self.scrollAreaWidget.setGeometry(QRect(0, 0, 780, 540))

        self.currentTrack = self.trackGroupBoxes[0]

    @property
    def name(self):
        return self.playlist.name

    def switch_tracks(self, direction):
        if slot_logs:
            print(f"[PLIST]{self.playlist.name} меняет {self.sender().composition} c {direction}")
        track = self.sender().composition
        self.playlist.swap(track, direction)
        self.update_list()

    def get_trackBox(self, composition: Composition):
        for box in self.trackGroupBoxes:
            if box.composition == composition:
                return box
        raise ValueError(f"{composition.name} not in playlist")

    def cur_track_upd(self):
        self.currentTrack = self.playlist.current_track

    def next_track(self):
        self.playlist.next_track()
        self.currentTrack = self.get_trackBox(self.playlist.current_track)

    def prev_track(self):
        self.playlist.previous_track()
        self.currentTrack = self.get_trackBox(self.playlist.current_track)

    def activate(self):
        if slot_logs:
            print(f"[PLIST]{self.playlist.name} хочет активироваться")
        self.want_to_activate.emit()

    def update_list(self):
        if slot_logs:
            print(f"[PLIST]{self.playlist.name} обновляет поля")
        self.trackGroupBoxes.clear()
        count = self.scrollAreaWidgetLayout.count()
        for i in range(0, count):
            item = self.scrollAreaWidgetLayout.itemAt(i)
            item.widget().deleteLater()
        for song in self.playlist:
            track = TrackGroupBox(song.data)
            track.switch_clicked.connect(self.switch_tracks)
            track.clicked.connect(self.song_picked)
            self.scrollAreaWidgetLayout.addWidget(track)
            self.trackGroupBoxes.append(track)
        self.list_updated.emit()

    def song_picked(self):
        self.playlist.current_track = self.sender().composition
        self.currentTrack = self.sender()
        if slot_logs:
            print(f"[PLIST]{self.playlist.name} включает {self.sender().composition}")
        self.list_updated.emit()

    def to_tab(self):
        return self, self.icon, self.name

    def append_song(self, song):
        self.playlist.append(song)
        self.scrollAreaWidgetLayout.addWidget(track := TrackGroupBox(song))
        self.trackGroupBoxes.append(track)
        track.switch_clicked.connect(self.switch_tracks)
        track.clicked.connect(self.song_picked)
        self.update_meta()

    def update_meta(self):
        self.playlist_meta.setText(str(self.playlist))

    def edit_playlist(self):
        if slot_logs:
            print(f"[PLIST]{self.playlist.name} хочет отредактироваться")

    def delete_playlist(self):
        print(f"[PLIST]{self.playlist.name} хочет исчезнуть")


class PlayListsTabWidget(QTabWidget):
    cur_playlist_updated = pyqtSignal(PlayListWidget)
    cur_playlist_want_to_activate = pyqtSignal(PlayListWidget)

    def __init__(self, playlists):
        super().__init__()

        self.tabs_count = len(playlists)
        self.playlists = playlists

        self.playlistLayouts = []
        for playlist in playlists:
            new_tab = PlayListWidget(playlist)
            new_tab.list_updated.connect(self.list_updated_slot)
            new_tab.want_to_activate.connect(self.list_activate_slot)
            # new_tab.cur_track_changed.connect(self.playlist_cur_track_changed_slot)
            self.addTab(*new_tab.to_tab())
            self.playlistLayouts.append(new_tab)

        self.addTab(QWidget(), 'Добавить плейлист')

        self.tabBarClicked.connect(self.if_add_playlist)

    def list_updated_slot(self):
        if slot_logs:
            print(f"[PLTAB] понял что {self.sender().playlist.name} обновился")
        self.cur_playlist_updated.emit(self.sender())
        self.cur_playlist_want_to_activate.emit(self.sender())

    def list_activate_slot(self):
        if slot_logs:
            print(f"[PLTAB] понял что {self.sender().playlist.name} хочет быть активным")
        self.cur_playlist_want_to_activate.emit(self.sender())

    def if_add_playlist(self, index):
        if index == self.tabs_count:
            new_playlist = make_random_playlist()
            self.add_playlist(new_playlist)

    def add_playlist(self, new_playlist):
        new_playlist_widget = PlayListWidget(new_playlist)
        new_playlist_widget.list_updated.connect(self.list_updated_slot)
        new_playlist_widget.want_to_activate.connect(self.list_activate_slot)

        self.removeTab(self.tabs_count)
        self.playlists.append(new_playlist)
        self.playlistLayouts.append(new_playlist_widget)

        self.addTab(*new_playlist_widget.to_tab())
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
                return True
        return False


class AudioLine(QGroupBox):
    def __init__(self, playlist):
        super().__init__()

        self.cur_playlist = playlist

        self.audioLineLayout = QVBoxLayout(self)  # Главный лейаут

        self.meta_layout = QHBoxLayout()  # Лейаут метаданных

        self.track_pic = QLabel()
        self.track_pic.setPixmap(self.cur_playlist.currentTrack.trackPicLabel.pixmap())

        self.text_meta_layout = QVBoxLayout()  # Лейаут текстовых данных трека

        font = QFont()
        font.setFamily("Comic Sans MS")
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(36)
        self.trackNameLabel = QLabel()
        self.trackNameLabel.setFont(font)

        self.trackAuthorLabel = QLabel()

        self.text_meta_layout.addWidget(self.trackNameLabel)
        self.text_meta_layout.addWidget(self.trackAuthorLabel)

        self.meta_layout.addWidget(self.track_pic)
        self.meta_layout.addLayout(self.text_meta_layout)
        self.meta_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.progressLayout = QHBoxLayout()  # Лейаут прогресса трека

        self.trackProgressSlider = QSlider()
        self.trackProgressSlider.setOrientation(Qt.Horizontal)
        self.trackDurationLabel = QLabel()

        # Добавляем в лейаут прогресса трека
        self.progressLayout.addWidget(self.trackProgressSlider)
        self.progressLayout.addWidget(self.trackDurationLabel)

        self.controlButtonsLayout = QHBoxLayout()  # Леаут кнопочек

        self.addToLikedPushButton = QPushButton("Нравица")
        self.prevTrackPushButton = QPushButton("←")
        self.playPushButton = QPushButton("►")
        self.pausePushButton = QPushButton("▌▐")
        self.nextTrackPushButton = QPushButton("→")

        self.player = QMediaPlayer()
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.cur_playlist.currentTrack.path)))
        self.player.positionChanged.connect(self.progress_tick)
        self.player.mediaStatusChanged.connect(self.playback_slot)

        # Добавляем в лейаут кнопочек
        self.controlButtonsLayout.addWidget(self.addToLikedPushButton)
        self.controlButtonsLayout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.controlButtonsLayout.addWidget(self.prevTrackPushButton)
        self.controlButtonsLayout.addWidget(self.playPushButton)
        self.controlButtonsLayout.addWidget(self.pausePushButton)
        self.controlButtonsLayout.addWidget(self.nextTrackPushButton)
        self.controlButtonsLayout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        crutchButton = QPushButton(" " * 7)
        crutchButton.setFlat(True)
        self.controlButtonsLayout.addWidget(crutchButton)

        # Добавляем в главный лейаут
        self.audioLineLayout.addLayout(self.meta_layout)
        self.audioLineLayout.addLayout(self.progressLayout)
        self.audioLineLayout.addLayout(self.controlButtonsLayout)

        self.pausePushButton.hide()
        self.trackNameLabel.setText(self.cur_playlist.currentTrack.name)
        self.trackAuthorLabel.setText(self.cur_playlist.currentTrack.artist)
        self.trackDurationLabel.setText(duration_from_seconds(self.cur_playlist.currentTrack.duration))
        self.trackProgressSlider.setRange(0, int(self.cur_playlist.currentTrack.duration))
        self.trackProgressSlider.setValue(0)

        self.playPushButton.clicked.connect(self.play)
        self.pausePushButton.clicked.connect(self.pause)
        self.prevTrackPushButton.clicked.connect(self.set_prev_track)
        self.nextTrackPushButton.clicked.connect(self.set_next_track)
        self.trackProgressSlider.sliderReleased.connect(self.upd_progress)

        self.update_fields()

    def set_playlist(self, playlist: PlayListWidget):
        if slot_logs:
            print(f"[ALINE] делает {playlist.name} активным ")
        self.cur_playlist = playlist
        self.update_fields()

    def update_fields(self):
        if slot_logs:
            print(f"[ALINE] обновляет свои поля")
        if self.player.media() != QMediaContent(QUrl.fromLocalFile(self.cur_playlist.currentTrack.path)):
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.cur_playlist.currentTrack.path)))
            self.track_pic.setPixmap(self.cur_playlist.currentTrack.trackPicLabel.pixmap())
            self.trackNameLabel.setText(self.cur_playlist.currentTrack.name)
            self.trackAuthorLabel.setText(self.cur_playlist.currentTrack.artist)
            self.trackDurationLabel.setText(duration_from_seconds(self.cur_playlist.currentTrack.duration))
            self.trackProgressSlider.setRange(0, int(self.cur_playlist.currentTrack.duration))
            self.trackProgressSlider.setValue(0)

            # self.pausePushButton.hide()
            # self.playPushButton.show()

    def play(self):
        self.playPushButton.hide()
        self.pausePushButton.show()
        self.player.play()

    def pause(self):
        self.pausePushButton.hide()
        self.playPushButton.show()
        self.player.pause()

    def set_prev_track(self):
        self.cur_playlist.prev_track()
        self.update_fields()
        self.play()

    def set_next_track(self):
        self.cur_playlist.next_track()
        self.update_fields()
        self.play()

    def progress_tick(self):
        self.trackProgressSlider.setValue(self.trackProgressSlider.value() + 1)

    def upd_progress(self):
        self.player.setPosition(self.trackProgressSlider.value() * 1000)

    def playback_slot(self, status):
        print(status)
        if status == QMediaPlayer.EndOfMedia:
            self.set_next_track()
            self.play()
        if status == 2:
            self.play()


class PlayerUI(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.rel = Relator(get_data_path() + '/playlists.json')

        self.playlists = self.rel.load_playlists()
        # self.playlists.append(make_random_playlist())
        # rel.save(self.playlists)
        self.tabs = PlayListsTabWidget(self.playlists)

        # self.tabs.tabBarClicked.connect(self.change_playlist)
        self.tabs.cur_playlist_updated.connect(self.upd_audioline)
        self.tabs.cur_playlist_want_to_activate.connect(self.activate_playlist)

        self.audioline = AudioLine(self.tabs.currentWidget())

        self.audioline.addToLikedPushButton.clicked.connect(self.like)

        self.verticalLayout_2.addWidget(self.tabs)
        self.verticalLayout_2.addWidget(self.audioline)

    def like(self):
        if "♥" not in self.tabs:
            self.tabs.add_playlist(make_liked_playlist(self.tabs.currentWidget().currentTrack.composition))
        else:
            liked_playlist = self.tabs.get_playlist_layout("♥")
            liked_playlist.append_song(self.tabs.currentWidget().currentTrack.composition)

    def activate_playlist(self, playlistWidget):
        if slot_logs:
            print(f"[UMAIN] хочет установить {playlistWidget.name} активным")
        self.audioline.set_playlist(playlistWidget)

    def upd_audioline(self):
        if slot_logs:
            print(f"[UMAIN] хочет обновить  поля [ALINE]")
        self.audioline.update_fields()


if __name__ == '__main__':
    app = QApplication(argv)
    ex = PlayerUI()
    ex.show()
    app.exec_()
    exit()
