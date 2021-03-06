from json import JSONDecodeError
from multiprocessing import Process
# from threading import Thread
import requests
import os
import time
from random import SystemRandom

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

rand = SystemRandom()


class TranscribeClient(Process):
    def __init__(self, media_path: str, client_id=-1):
        super(TranscribeClient, self).__init__()
        self.media_path = media_path
        self.corpus_id = None
        self.client_id = client_id

    def transcribe_file(self):
        url = "http://localhost:8080/transcribe_file"
        with open(self.media_path, 'rb') as f:
            r = requests.post(url, data=f)
            try:
                comeback = r.json()
            except JSONDecodeError:
                self.transcribe_file()
                return
            self.corpus_id = comeback["corpus_id"]
            print("client id", self.client_id, "queue", comeback["queue"], "|\t", self.corpus_id)

    def poll_transcript(self):
        url = "http://localhost:8080/get_transcript"
        params = {
            "corpus_id": self.corpus_id
        }
        r = requests.get(url, params=params)
        comeback = r.json()
        c = int(comeback["complete"])
        queue = comeback["queue"]
        while c != 1:
            time.sleep(5)
            r = requests.get(url, params=params)
            comeback = r.json()
            if "queue" in comeback:
                queue = comeback["queue"]
            c = int(comeback["complete"])
        print(self.client_id, "Completed.")

    def run(self) -> None:
        print("Starting: ", self.client_id)
        self.transcribe_file()
        self.poll_transcript()


def up_sample_dataset(out_sz: int, dataset: list) -> list:
    in_sz = len(dataset)
    sample = []

    for i in range(out_sz):
        random_idx = rand.randrange(0, in_sz)
        sample.append(dataset[random_idx])
    return sample


if __name__ == '__main__':
    start = time.time()
    print("CUDA batched-decoder benchmark:")

    # data_sizes = [1, 5, 10, 15, 20, 25, 50]
    data_sizes = [20, 25, 50]

    batch_size = 20
    bench_path = "benchmark_batch_" + str(batch_size) + ".txt"
    if os.path.exists(bench_path):
        os.remove(bench_path)

    batches = {}
    for ds in data_sizes:
        fd = open("benchmark_data_" + str(ds) + ".txt", "r")
        batches[str(ds)] = fd.readlines()

    for data_size in data_sizes:
        benchmark_log = open(bench_path, "a")
        batch = batches[str(data_size)]
        for media in batch:
            media = media[:len(media) - 1]
            if not os.path.exists(media):
                raise Exception("Benchmark file missing: " + media)
        bench_workers = []
        for idx, media in enumerate(batch):
            media = media[:len(media) - 1]
            bench_workers.append(TranscribeClient(media, idx))

        for worker in bench_workers:
            worker.start()

        for worker in bench_workers:
            worker.join()
        time_spent = str(time.time() - start)
        print("time spent: " + time_spent)
        benchmark_log.write("data size: " + str(data_size) + ", time spent: " + time_spent + "\n")
        benchmark_log.close()
