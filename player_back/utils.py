import os


def get_data_path():
    cur_dir = os.getcwd()
    if not cur_dir.endswith('audioPlayer_algo2QT'):
        res = []
        for folder in cur_dir.split("\\"):
            if folder != 'audioPlayer_algo2QT':
                res.append(folder)
            else:
                res.extend([folder, 'data'])
                break
        return '\\'.join(res)
    else:
        return os.path.join(cur_dir, 'data')


def duration_from_seconds(s):
    """Module to get the convert Seconds to a time like format."""
    s = s
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)

    if h != 0:
        timelapsed = f"{int(h):02}:{int(m):02}:{int(s):02}"
    else:
        timelapsed = f"{int(m):02}:{int(s):02}"

    return timelapsed


if __name__ == '__main__':
    print(get_data_path())
