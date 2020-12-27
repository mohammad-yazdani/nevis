from dataclasses import dataclass
from threading import Thread
from typing import List
from lib.audio import Audio
from tools.file_io  import delete_if_exists
import os

MAX_BATCH_SIZE = 10     # Max number of Decodings in a batch 

class BatchFull(Exception):
    def __init__(self, *args: object) -> None:
        super(BatchFull, self).__init__(*args)


@dataclass(order=True)
class ToDecode:

    def __init__(self, wav_path: str, duration: int, priority: int = 1) -> None:
        super().__init__()
        self.priority = priority
        self.wav_path = wav_path
        self.duration = duration
        self.basename = os.path.basename(wav_path)


class Batch(Thread):
    batch_idx: int = 0

    def __init__(self) -> None:
        super(Batch, self).__init__()
        self.batch_id = 0
        Batch.batch_idx += 1
        self.batch: List[ToDecode] = []
        self.batch_path = os.path.join(Audio.get_prefix(), "batch", str(self.batch_id))

    def add(self, td: ToDecode):
        if len(self.batch) == MAX_BATCH_SIZE:
            raise BatchFull
        else:
            self.batch.append(td)

    def run(self):
        if len(self.batch) == 0:
            print(os.getpid(), self.native_id, "empty batch")
            return
        else:
            delete_if_exists(self.batch_path)
            os.mkdir(self.batch_path)
            for d in self.batch:
                os.symlink(d.wav_path, os.path.join(self.batch_path, d.basename))
            # TODO : Do decoding
            # TODO : Do alignment
