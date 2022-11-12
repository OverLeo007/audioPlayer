import io
import logging
import os

import eyed3

from player_back import track_path
from player_back.utils import duration_from_seconds, get_data_path


class Composition:
    def __init__(self, path):
        audio = self.loader(path)
        self.path = path
        self.name = audio.tag.title
        self.artist = audio.tag.artist
        self.duration = audio.info.time_secs
        try:
            self.img = audio.tag.images[0].image_data
        except Exception as e:
            with open(get_data_path() + "\\unknown_img.png", 'rb') as file:
                self.img = file.read()

    def loader(self, path):
        log_stream = io.StringIO()
        logging.basicConfig(stream=log_stream, level=logging.INFO)
        audiofile = eyed3.load(path)
        llog = log_stream.getvalue()
        if llog:
            log_stream.truncate(0)
        return audiofile

    def save_img(self):
        with open(get_data_path() + '\\testimg.png', 'wb') as file:
            file.write(self.img)

    def __repr__(self):
        return f'{self.artist} - {self.name} {duration_from_seconds(self.duration)}'


def get_compositions(paths):
    return [Composition(t_path) for t_path in paths]


if __name__ == '__main__':
    new_comp = Composition(r'C:\Users\leva\PycharmProjects\audioPlayer_algo2QT\tracks\salamisound-4960259-open-door'
                           r'-lock-knock.mp3')
    print(new_comp.img)
    new_comp.save_img()
