from os import listdir

track_path = r"C:\Users\leva\PycharmProjects\audioPlayer_algo2QT\tracks"

list_of_all = [f"{track_path}\\{track}" for track in listdir(track_path)]
