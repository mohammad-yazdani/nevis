from lib.audio import Audio
from lib.batch import Batch, BatchFull
from multiprocessing import Process, Queue
from threading import Event
from queue import Empty
import os

THRESHOLD = 1.5         # In seconds
MAX_READY = 1000        # Max number of items in queue

class TimedQueue(Process):    
    def __init__(self):
        super(TimedQueue, self).__init__()
        self.ready = Queue()
        self.exit_flag = Event()

    def run(self):
        print(os.getpid(), "run")
        while not self.exit_flag.wait(timeout=THRESHOLD):
            self.make_batch()

    def accept(self, media: str):
        self.ready.put_nowait(Audio.prepare(media))

    def make_batch(self):
        batch = Batch()
        try:
            while True:
                decoding = self.ready.get_nowait()
                batch.add(decoding)
        except Empty:
            pass
        except BatchFull:
            pass
        # Non-blocking
        batch.start()
