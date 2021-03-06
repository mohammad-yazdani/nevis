from lib.decoder import Decoder
import os
from random import randint
from typing import List
from time import sleep

from lib.batch import ToDecode
from lib.timed_queue import TimedQueue

import pickle

def main():
    print(os.getpid(), "main")

if __name__ == "__main__":
    num_proc = 4
    pool: List[TimedQueue] = []

    # Set off procs
    for i in range(num_proc):
        pool.append(TimedQueue(Decoder("", 32423)))
        pool[i].start()

    dummy_path = "/root/audio/test"
    for i in range(5000):
        if i % 20 == 0:
            sleep(5)
        td = ToDecode(dummy_path + str(i) + ".wav", randint(1, 10000))
        pickle.dumps(ToDecode)
        pool[i % num_proc].accept("td", Decoder("", 32423))

    # Wait for finish
    for i in range(num_proc):
        pool.append(TimedQueue())
        pool[i].join()

    main()
