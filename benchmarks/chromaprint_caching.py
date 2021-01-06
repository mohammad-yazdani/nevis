import os
import time
from json import JSONDecodeError
from multiprocessing import Process
from random import SystemRandom
import json

import acoustid
import chromaprint
import requests

MEDIA_FILES = [
    "/mnt/NVSTORE/corpora/raw_audio/17_The_Peloponnesian_War_Part_I.wav",
    "/mnt/NVSTORE/corpora/raw_audio/27_Vibration_of_Continuous_Structures_Strings_Beams_Rods_etc.wav",
    "/mnt/NVSTORE/corpora/raw_audio/30_Activation_Functions_Softmax_Activation_Detail_Explanation.wav",
    "/mnt/NVSTORE/corpora/raw_audio/Aalto_Talk_with_Linus_Torvalds.wav",
    "/mnt/NVSTORE/corpora/raw_audio/DODGE_HEMI_-_Everything_You_Need_To_Know__Up_To_Speed.wav",
    "/mnt/NVSTORE/corpora/raw_audio/How_Many_Holes_Does_a_Human_Have.wav",
    "/mnt/NVSTORE/corpora/raw_audio/Least_Recently_Used__Page_Replacement_Algorithm__Operating_System.wav",
    "/mnt/NVSTORE/corpora/raw_audio/Lecture_1_Introduction_to_Power_and_Politics_in_World.wav",
    "/mnt/NVSTORE/corpora/raw_audio/Matrix_vector_products__Vectors_and_spaces__Linear_Algebra__Khan_Academy.wav",
    "/mnt/NVSTORE/corpora/raw_audio/The_LG_Wing_is_Like_No_Other_Smartphone.wav",
    "/mnt/NVSTORE/corpora/raw_audio/The_W12_Engine_-_The_Science_EXPLAINED.wav",
    "/mnt/NVSTORE/corpora/raw_audio/rec05.wav"
]

CACHE_TEST = [
    "/mnt/NVSTORE/corpora/raw_audio/The_LG_Wing_is_Like_No_Other_Smartphone.wav",
    "/mnt/NVSTORE/corpora/raw_audio/The_W12_Engine_-_The_Science_EXPLAINED.wav",
    "/mnt/NVSTORE/corpora/raw_audio/rec05.wav"
]

WORDS = [
    "Shazam", "builds", "fingerprint", "catalog", "hash", "table", "frequency", "spectrogram",
    "rather", "intensity", "anchor"
]

rand = SystemRandom()

model_quality = []


class TranscribeClient(Process):
    def __init__(self, media_path: str, client_id=-1, use_cache: bool = True):
        super(TranscribeClient, self).__init__()
        self.media_path = media_path
        self.fp = fingerprint(media_path)
        self.corpus_id = None
        self.client_id = client_id
        self.corpus = None
        self.use_cache = use_cache

    def transcribe_file(self) -> None:
        if self.use_cache:
            cached_url = "http://localhost:8080/cached_transcript"
            params = {
                "fingerprint": self.fp
            }
            r = requests.get(cached_url, params=params)
            try:
                comeback = r.json()
                c = int(comeback["complete"])
                if c == 1:
                    self.corpus = comeback
                    print("client id", self.client_id, "transcribed from cache")
                    return
            except JSONDecodeError:
                pass

        url = "http://localhost:8080/transcribe_file"
        with open(self.media_path, 'rb') as f:
            params = {}
            r = requests.post(url, params=params, data=f)
            try:
                comeback = r.json()
            except JSONDecodeError:
                self.transcribe_file()
                return
            self.corpus_id = comeback["corpus_id"]
            print("client id", self.client_id, "queue", comeback["queue"], "|\t", self.corpus_id)

    def poll_transcript(self) -> None:
        if self.corpus is not None:
            return

        url = "http://localhost:8080/get_transcript"
        params = {
            "corpus_id": self.corpus_id
        }
        if self.use_cache:
            params["fingerprint"] = self.fp
        r = requests.get(url, params=params)
        comeback = r.json()
        c = int(comeback["complete"])
        while c != 1:
            time.sleep(5)
            r = requests.get(url, params=params)
            comeback = r.json()
            c = int(comeback["complete"])
        self.corpus = comeback
        print(self.client_id, "Completed,", "quality:", comeback["quality"])
        model_quality.append(comeback["quality"])

    def send_feedback(self):
        params = {
            "corpus_id": self.corpus_id
        }
        url = "http://localhost:8080/submit_feedback"
        max_words_to_submit = 10
        words_to_submit = rand.randrange(0, max_words_to_submit)
        words_to_submit = WORDS[words_to_submit:]
        r = requests.post(url, params=params, data=json.dumps({
            "corrections": words_to_submit
        }))
        try:
            r.json()
        except JSONDecodeError:
            pass
        print("client id", self.client_id, "retraining")

    def run(self) -> None:
        print("Starting: ", self.client_id)
        self.transcribe_file()
        self.poll_transcript()
        self.send_feedback()


def up_sample_dataset(out_sz: int, dataset: list) -> list:
    in_sz = len(dataset)
    sample = []

    for i in range(out_sz):
        random_idx = rand.randrange(0, in_sz)
        sample.append(dataset[random_idx])
    return sample


def fingerprint(path: str, length: int = 120, raw: bool = False) -> str:
    duration, fp = acoustid.fingerprint_file(path, length)
    if raw:
        raw_fp = chromaprint.decode_fingerprint(fp)[0]
        fp = ','.join(map(str, raw_fp))
    return fp


if __name__ == '__main__':
    start = time.time()
    print("CUDA batched-decoder benchmark:")
    data_sizes = [10, 20, 50]

    bench_path = "benchmark_cache.txt"
    if os.path.exists(bench_path):
        os.remove(bench_path)

    for data_size in data_sizes:
        benchmark_log = open(bench_path, "a")
        batch = up_sample_dataset(data_size, MEDIA_FILES)
        for media in batch:
            # media = media[:len(media) - 1]
            if not os.path.exists(media):
                raise Exception("Benchmark file missing: " + media)
        bench_workers = []
        for idx, media in enumerate(batch):
            # media = media[:len(media) - 1]
            bench_workers.append(TranscribeClient(media, idx))

        for worker in bench_workers:
            worker.start()

        for worker in bench_workers:
            worker.join()
        time_spent = str(time.time() - start)
        print("time spent: " + time_spent)
        benchmark_log.write("data size: " + str(data_size) + ", time spent: " + time_spent + "\n")
        benchmark_log.close()

    print(model_quality)
