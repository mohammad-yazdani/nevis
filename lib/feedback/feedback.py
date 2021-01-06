import os
from threading import Thread
from typing import List

from tools.shexec import Shell, ShellFail

WORDS_COMMAND = "grep -oE \"[A-Za-z\\-\\']{3,}\" FEEDBACK_PATH | tr '[:lower:]' '[:upper:]' | sort | uniq > " \
                "/opt/kaldi/egs/vystadial_en/s5/common/words.txt"
RETRAIN_SCRIPT = "./lib/feedback/retrain.sh"


class FeedbackAgent(Thread):

    def __init__(self, batch_id: int, corpus_id: str, corrections: List[str], callback):
        super(FeedbackAgent, self).__init__()
        self.batch_id = batch_id
        self.corpus_id = corpus_id
        self.callback = callback

        if corpus_id != "":
            corpus_id = "_" + corpus_id
        corpus_path = os.path.join("/tmp/results/aspire/" + str(batch_id), "0", "trans" + corpus_id)
        feedback_command = WORDS_COMMAND.replace("FEEDBACK_PATH", corpus_path)
        try:
            shell = Shell()
            shell.shell_execute(feedback_command)
        except ShellFail as sf:
            sf.why()

        words_set = "/opt/kaldi/egs/vystadial_en/s5/common/words.txt"
        with open(words_set, "a") as wsfd:
            for w in corrections:
                wsfd.write(w.upper() + "\n")

    def run(self) -> None:
        print("Thread ", self, "running retraining job on batch:", self.batch_id, "corpus:", self.corpus_id)
        try:
            shell = Shell()
            shell.shell_execute(RETRAIN_SCRIPT)
            self.callback()
        except ShellFail as sf:
            sf.why()
