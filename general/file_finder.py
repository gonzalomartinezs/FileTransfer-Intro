import os
from os.path import isfile, join


def dir_exists(path):
    try:
        os.listdir(path)
    except FileNotFoundError:
        return False
    return True


def file_exists(filepath, filename):
    content = os.listdir(filepath)
    files = [file for file in content
             if file == filename and isfile(join(filepath, filename))]

    return len(files) != 0
