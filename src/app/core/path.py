import os


def root_path():
    FILE_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.abspath(os.path.join(FILE_DIR, '..'))
    return ROOT_DIR
