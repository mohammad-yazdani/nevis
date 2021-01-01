import os
import shutil

def delete_if_exists(filepath):
    if os.path.exists(filepath):
        if os.path.isdir(filepath):
            shutil.rmtree(filepath)
        else:
            os.remove(filepath)
