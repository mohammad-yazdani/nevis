import os
import shutil
from dataclasses import dataclass
from threading import Thread
from typing import List

from tools.file_io import delete_if_exists

from lib.decoder import Decoder


class BatchFull(Exception):
    def __init__(self, *args: object) -> None:
        super(BatchFull, self).__init__(*args)


@dataclass(order=True)
class ToDecode:

    def __init__(self, wav_path: str, duration: float, corpus_id: str, priority: int = 1) -> None:
        super().__init__()
        self.wav_path = wav_path
        self.duration = duration
        self.priority = priority
        self.basename = str(os.path.basename(wav_path))
        self.corpus_id = corpus_id


class Batch(Thread):
    batch_prefix: str = "/root/audio/batch"
    batch_idx: int = 0

    def __init__(self, decoder: Decoder, batch_id: int, reciever, max_batch_size) -> None:
        super(Batch, self).__init__()
        self.batch_id = batch_id
        self.batch: List[ToDecode] = []
        self.decoder = decoder
        self.recv = reciever
        self.max_batch_size = max_batch_size

    def add(self, td: ToDecode) -> None:
        if len(self.batch) == self.max_batch_size:
            raise BatchFull
        else:
            self.batch.append(td)

    def is_empty(self) -> bool:
        return len(self.batch) == 0

    def run(self) -> None:
        if len(self.batch) > 0:

            delete_if_exists(os.path.join(Batch.batch_prefix + str(self.batch_id)))
            os.mkdir(os.path.join(Batch.batch_prefix + str(self.batch_id)))
            for d in self.batch:
                wav_path = os.path.join(Batch.batch_prefix + str(self.batch_id), d.basename + ".wav")
                shutil.move(d.wav_path, wav_path)
            batch_out = self.decoder.decode_batch(self.batch_id)
            for key in batch_out.keys():
                self.recv(key, batch_out[key])
