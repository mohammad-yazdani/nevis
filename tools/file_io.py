import os


def delete_if_exists(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)
