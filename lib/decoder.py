from subprocess import Popen, PIPE
from typing import List, Tuple
import os
import logging

class Decoder:
    def __init__(self, name: str, bit_rate: int, iteration: int = 1, max_active: int = 20000, max_batch_size=100) -> None:
        super().__init__()
        self.name = name
        self.bit_rate = bit_rate
        
        self.env = os.environ.copy()
        self.env["ITERATIONS"] = str(iteration)
        self.env["MAX_ACTIVE"] = str(max_active)
        self.env["MAX_BATCH_SIZE"] = str(max_batch_size)

        self.model_dir = os.path.join("/workspace/nvidia-examples/", name.lower())
        self.result_dir = os.path.join("/tmp/results/", name.lower())
        self.prep_command = "prepare_data.sh"
        self.batch_command = "run_benchmark.sh"

        self.last_run = None

    def initalize(self) -> None:
        prep_process = Popen(["/bin/bash", self.prep_command], stdin=PIPE, stderr=PIPE, cwd=self.model_dir)        
        stdout, stderr = prep_process.communicate()
        logging.debug(stdout)
        logging.debug(stderr)

    def decode_batch(self, batch_path: str) -> None:
        # set environment, start new shell
        batch_env = self.env
        batch_env["DATASET"] = batch_path
        prep_process = Popen(["/bin/bash", self.batch_command], stdin=PIPE, stderr=PIPE, env=batch_env, cwd=self.model_dir)
        stdout, stderr = prep_process.communicate()
        logging.debug(stdout)
        logging.debug(stderr)

        if self.last_run is not None:
            self.last_run += 1
        else:
            self.last_run = 0

    def clear_results(self) -> None:
        if os.path.exists(self.result_dir):
            os.rmdir(self.result_dir)

    def get_trans(self, batch_id: int, corpus_id: str, iter_id: int = 0) -> List[str]:
        trans_file = os.path.join(self.result_dir, str(batch_id), str(iter_id), "trans_" + corpus_id)
        f = open(trans_file)
        transcript: str = f.read().split(" ", 1)[1]
        f.close()
        return transcript

    # TODO : This alignment logic needs a review
    def get_alignment(self, batch_id: int, corpus_id: str, iter_id: int = 0) -> Tuple[List[int], float]:
        # batch_env = self.env
        prep_process = Popen(["/usr/bin/gzip", "-d", os.path.join(self.result_dir, str(batch_id), str(iter_id), "lat_aligned.gz")], stdin=PIPE)
        stdout, stderr = prep_process.communicate()
        logging.debug(stdout)
        logging.debug(stderr)

        ctm_file = os.path.join(self.result_dir, str(batch_id), str(iter_id), corpus_id + ".ctm")
        
        lattice_align_command: str = ""
        lattice_align_command += "/opt/kaldi/src/latbin/lattice-align-words-lexicon --partial-word-label=4324 /workspace/models/aspire/data/lang_chain/phones/align_lexicon.int /workspace/models/aspire/final.mdl"
        lattice_align_command += (" ark:" + os.path.join(self.result_dir, str(batch_id), str(iter_id), "lat_aligned"))
        lattice_align_command += " ark:- | /opt/kaldi/src/latbin/lattice-1best ark:- ark:- | /opt/kaldi/src/latbin/nbest-to-ctm ark:- "
        lattice_align_command += ctm_file
        # prep_process = Popen(lattice_align_command, stdin=PIPE, env=batch_env)
        prep_process = Popen(lattice_align_command, stdin=PIPE, shell=True)
        stdout, stderr = prep_process.communicate()
        logging.debug(stdout)
        logging.debug(stderr)

        trans_file = os.path.join(self.result_dir, str(batch_id), str(iter_id), "trans_int_combined")
        idxwords = open(trans_file).read()
        rawlats = open(ctm_file).readlines()

        lats = []
        words = self.get_trans(batch_id, corpus_id)

        idx = idxwords.split()
        parse_list = idx
        idx = []
        for p in parse_list:
            try:
                idx.append(int(p))
            except ValueError:
                pass
        for l in rawlats:
	        ln_data = l.split()[3:]
	        lats.append([float(ln_data[0]), int(ln_data[1])])

        word_table = dict()
        alignment = []
        for i in range(min(len(words), len(idx))):
            wt_idx = idx[i]
            word_table[wt_idx] = words[i]
        offset = 0.0
        for i in range(min(len(words), len(idx))):
            offset += lats[i][0]
            alignment.append([word_table[lats[i][1]], offset - lats[i][0]])

        return alignment, offset
