from lib.decoder import Decoder
from lib.audio import Audio
from lib.batch import Batch, BatchFull, ToDecode
from threading import Event, Thread, Lock
from queue import Queue, Empty
from typing import Tuple, Dict
import os

THRESHOLD = 20          # In seconds
MAX_READY = 1000        # Max number of items in queue
MAX_BATCH_SIZE = 5      # Max number of Decodings in a batch

class TimedQueue(Thread):
    def __init__(self, decoder: Decoder):
        super(TimedQueue, self).__init__()
        self.ready: Queue[ToDecode] = Queue()
        self.exit_flag = Event()
        self.decoder = decoder
        self.batches = 0
        self.output: Dict[int, Dict[str, object]] = {}
        self.queue_lk = Lock()
        self.active = 0
        self.corpus_map: Dict[str, int] = {}

    def run(self) -> None:
        print("TimedQueue", os.getpid(), "run")
        while not self.exit_flag.wait(timeout=THRESHOLD):
            self.make_batch()

    # TODO : Review the atomicity of these methods
    def accept(self, media: bytes, decoder: Decoder) -> str:
        td: ToDecode = Audio.prepare(media, decoder.bit_rate)
        self.ready.put(td)
        self.active += 1
        return td.corpus_id

    def make_batch(self) -> None:
        self.queue_lk.acquire(blocking=True)
        batch = Batch(self.decoder, self.batches, self.recieve, MAX_BATCH_SIZE)
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
        self.queue_lk.release()

        # Non-blocking
        batch.start()

    def recieve(self, corpus_id: str, transcript: object) -> None:
        self.active -= 1
        self.output[corpus_id] = transcript

    def get_corpus_batch(self, corpus_id: str) -> int:
        return self.corpus_map[corpus_id]
