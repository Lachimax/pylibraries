from sys import platform
import os


def clear_empty_paths(path):
    for next_path in filter(lambda d: os.path.isdir(path + "\\" + d), os.listdir(path)):
        print(next_path)
        next_path = path + "\\" + next_path
        clear_empty_paths(next_path)

    if os.path.isdir(path):
        if len(os.listdir(path)) == 0:
            print("Attempting removal of", path)
            os.removedirs(path)


def sanitise_path(path):
    path = path.replace(";", "_").replace("|", "_").replace(",", "_").replace('"', "_").replace("'", "_")
    path = path.replace(":", "_").replace("*", "_").replace("/", "_").replace("\\", "")
    path = path.replace("^", "_").replace("<", "(").replace(">", ")").replace("?", "_")
    while path[-1] == " ":
        path = path[:-1]
    return path


def check_trailing_slash(path):
    path = str(path)
    if platform == 'linux':
        char = '/'
    else:
        char = '\\'
    if path != "":
        if path[-1] != char:
            path += char
    return path


def get_filetype(path):
    pos = -1
    while abs(pos) <= len(path):
        if path[pos] == '.':
            return path[pos + 1:]
        pos = pos - 1
    return 'directory'


def get_filename(path):
    pos = -1
    while abs(pos) <= len(path):
        if path[pos] == '\\':
            return path[pos + 1:]
        pos = pos - 1
    return path
