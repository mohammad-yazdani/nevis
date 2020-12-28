from lib.batch import Batch
from subprocess import Popen, PIPE
from typing import List
import os
import logging

class Decoder:
    def __init__(self, name: str, iteration: int = 1, max_active: int = 20000, max_batch_size=100) -> None:
        super().__init__()
        self.name = name
        
        self.env = os.environ.copy()
        self.env["ITERATIONS"] = iteration
        self.env["MAX_ACTIVE"] = max_active
        self.env["MAX_BATCH_SIZE"] = max_batch_size

        self.model_dir = os.path.join("/workspace/nvidia-examples/", name.lower())
        self.result_dir = os.path.join("/tmp/results/", name.lower())
        self.prep_command = os.path.join(self.model_dir, "prepare_data.sh")
        self.batch_command = os.path.join(self.model_dir, "run_benchmark.sh")

        self.last_run = None

    def initalize(self) -> None:
        prep_process = Popen(["/bin/bash", self.prep_command], stdin=PIPE, check_call=True, check_output=True)        
        stdout, stderr = prep_process.communicate()
        logging.debug(stdout)
        logging.debug(stderr)

    def decode_batch(self, batch: Batch) -> list:
        # set environment, start new shell
        batch_env = self.env
        batch_env["DATASET"] = batch.batch_path
        prep_process = Popen(["/bin/bash", self.prep_command], stdin=PIPE, env=batch_env, check_call=True, check_output=True)
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

    def get_trans(self, batch_id: int = None, id: int = 0) -> List[str]:
        if batch_id is None:
            batch_id = self.last_run
        trans_file = os.path.join(self.result_dir, str(batch_id), str(id), "trans")
        f = open(trans_file)
        transcript: str = f.read()
        f.close()
        return transcript

    def get_alignment(self, batch_id: int = None, id: int = 0) -> List[int]:
        if batch_id is None:
            batch_id = self.last_run
        trans_file = os.path.join(self.result_dir, str(batch_id), str(id), "trans_int_combined")
        f = open(trans_file)
        transcript: str = f.read()
        f.close()
        tokens = transcript.split()
        return list(map(lambda x: int(x), tokens))
