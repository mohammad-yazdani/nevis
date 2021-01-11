import os
from threading import Thread, Lock
from typing import List

from tools.shexec import Shell, ShellFail

WORDS_COMMAND = "grep -oE \"[A-Za-z\\-\\']{3,}\" FEEDBACK_PATH | tr '[:lower:]' '[:upper:]' | sort | uniq > " \
                "/opt/kaldi/egs/aspire/s5/words.txt"
RETRAIN_SCRIPT = "./lib/feedback/retrain.sh"


class FeedbackAgent(Thread):

    def __init__(self, batch_id: int, corpus_id: str, corrections: List[str]):
        super(FeedbackAgent, self).__init__()
        self.batch_id = batch_id
        self.corpus_id = corpus_id
        self.corpus_ext = corrections
        self.lk: Lock = None

    def run(self) -> None:
        self.lk.acquire(blocking=True)

        if self.corpus_id != "":
            self.corpus_id = "_" + self.corpus_id
        corpus_path = os.path.join(
            "/tmp/results/aspire/" + str(self.batch_id), "0", "trans" + self.corpus_id)
        feedback_command = WORDS_COMMAND.replace("FEEDBACK_PATH", corpus_path)
        try:
            shell = Shell()
            shell.shell_execute(feedback_command)
        except ShellFail as sf:
            sf.why()

        words_set = "/opt/kaldi/egs/aspire/s5/words.txt"
        try:
            with open(words_set, "a") as wsfd:
                for w in self.corpus_ext:
                    wsfd.write(w.upper() + "\n")
        except:
            print("No corrections")
            self.lk.release()
            return

        print("Thread ", self, "running retraining job on batch:",
              self.batch_id, "corpus:", self.corpus_id)
        shell = Shell()
        while True:
            try:
                print(shell.shell_execute(RETRAIN_SCRIPT))
                break
            except ShellFail as sf:
                sf.why()
        
        self.lk.release()
