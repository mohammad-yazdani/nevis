import os
from typing import Set


class ReTrainCorpus:
    def __init__(self, batch_id: int, corpus_id: str) -> None:
        super().__init__()
        self.corpus_path = os.path.join("/root/audio/batch" + str(batch_id), "tran_" + corpus_id + ".txt")
        self.corpus_splitted = open(self.corpus_path, "r").read().split()
        self.corpus_set: Set[str] = set()
        for w in self.corpus_splitted:
            self.corpus_set.add(w)
