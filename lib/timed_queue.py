from lib.decoder import Decoder
from lib.audio import Audio
from lib.batch import Batch, BatchFull, ToDecode
from threading import Event, Thread
from queue import Queue, Empty
from typing import Tuple, Dict
import os

THRESHOLD = 20          # In seconds
MAX_READY = 1000        # Max number of items in queue

class TimedQueue(Thread):
    def __init__(self, decoder: Decoder):
        super(TimedQueue, self).__init__()
        self.ready = Queue()
        self.exit_flag = Event()
        self.decoder = decoder
        self.batches = 0
        self.output: Dict[int, Dict[str, object]] = {}

    def run(self) -> None:
        print(os.getpid(), "run")
        while not self.exit_flag.wait(timeout=THRESHOLD):
            self.make_batch()

    # TODO : Review the atomicity of these methods
    def accept(self, media: str, decoder: Decoder) -> Tuple[int, str]:
        td: ToDecode = Audio.prepare(media, decoder.bit_rate)
        td.batch_id = self.batches
        self.ready.put_nowait(td)
        return td.batch_id, td.corpus_id

    def make_batch(self) -> None:
        batch = Batch(self.decoder, self.batches, self.recieve)
        try:
            while True:
                decoding = self.ready.get_nowait()
                batch.add(decoding)
        except Empty:
            pass
        except BatchFull:
            pass
        
        if batch.is_empty():
            return

        self.batches += 1
        # Non-blocking
        batch.start()

    def recieve(self, batch_id: int, batch_out: object) -> None:
        self.output[batch_id] = batch_out
