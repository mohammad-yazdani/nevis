from dataclasses import dataclass, field
from threading import Thread
from typing import List
import os

MAX_BATCH_SIZE = 10     # Max number of Decodings in a batch 

class BatchFull(Exception):
    def __init__(self, *args: object) -> None:
        super(BatchFull, self).__init__(*args)

@dataclass(order=True)
class ToDecode:
    priority: int
    wav_path: str=field(compare=False)
    duration: int=field(compare=False)

    def __init__(self, wav_path: str, duration: int, priority: int = 1) -> None:
        super().__init__()
        self.priority = priority
        self.wav_path = wav_path
        self.duration = duration

class Decode(Thread):
    batch: List[ToDecode]

    def __init__(self) -> None:
        super(Decode, self).__init__()
        self.batch = []

    def add(self, td: ToDecode):
        if len(self.batch) == MAX_BATCH_SIZE:
            raise BatchFull
        else:
            self.batch.append(td)

    def run(self):
        # print(os.getpid(), self.native_id, "run")
        
        if len(self.batch) == 0:
            print(os.getpid(), self.native_id, "empty batch")
            return
        for d in self.batch:
            print(os.getpid(), self.native_id, d.wav_path, d.duration)
