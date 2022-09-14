import logging
import os
from queue import Queue, Empty
from threading import Event, Thread, Lock
from typing import Dict

from lib.audio import Audio
from lib.batch import Batch, ToDecode
from lib.decoder import Decoder

THRESHOLD = 20  # In seconds
MAX_READY = 1000  # Max number of items in queue
MAX_BATCH_SIZE = 10  # Max number of Decoding in a batch


class TimedQueue(Thread):
    def __init__(self, decoder: Decoder):
        super(TimedQueue, self).__init__()
        self.ready: Queue[ToDecode] = Queue()
        self.exit_flag = Event()
        self.decoder = decoder
        self.batches = 0
        self.output: Dict[str, Dict[str, object]] = {}
        self.queue_lk = Lock()
        self.active = 0
        self.corpus_map: Dict[str, int] = {}

    def run(self) -> None:
        logging.debug("TimedQueue\t" + str(os.getpid()) + " run")
        while not self.exit_flag.wait(timeout=THRESHOLD):
            self.make_batch()
        logging.debug("TimedQueue\t" + str(os.getpid()) + "terminated")

    def accept(self, media: bytes, decoder: Decoder) -> str:
        td: ToDecode = Audio.prepare(media, decoder.bit_rate)
        self.ready.put_nowait(td)
        self.active += 1
        return td.corpus_id

    def make_batch(self) -> None:
        batch = Batch(self.decoder, self.batches, self.receive, MAX_BATCH_SIZE)
        try:
            for _ in range(MAX_BATCH_SIZE):
                decoding = self.ready.get_nowait()
                self.corpus_map[decoding.corpus_id] = batch.batch_id
                batch.add(decoding)
        except Empty:
            pass

        if batch.is_empty():
            return

        self.batches += 1

        # Non-blocking
        batch.start()

    def receive(self, corpus_id: str, transcript: Dict[str, object]) -> None:
        self.active -= 1
        self.output[corpus_id] = transcript

    def get_corpus_batch(self, corpus_id: str) -> int:
        return self.corpus_map[corpus_id]
