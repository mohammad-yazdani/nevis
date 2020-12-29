from dataclasses import dataclass
from lib.decoder import Decoder
from threading import Thread, Condition
from typing import List
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
        self.wav_path = wav_path
        self.duration = duration
        self.priority = priority
        self.basename = str(os.path.basename(wav_path))
        self.corpus_id = None
        self.batch_id = None


class Batch(Thread):
    batch_idx: int = 0
    
    def __init__(self, decoder: Decoder, batch_id: int) -> None:
        super(Batch, self).__init__()
        self.batch_id = batch_id
        self.batch: List[ToDecode] = []
        self.batch_path = os.path.join("/root/audio/batch" + str(self.batch_id))
        self.decoder = decoder

    def add(self, td: ToDecode) -> None:
        if len(self.batch) == MAX_BATCH_SIZE:
            raise BatchFull
        else:
            self.batch.append(td)

    def run(self) -> None:
        if len(self.batch) > 0:

            delete_if_exists(self.batch_path)
            os.mkdir(self.batch_path)
            for d in self.batch:
                os.symlink(d.wav_path, os.path.join(self.batch_path, d.basename))
            self.decoder.decode_batch(self.batch_path)
