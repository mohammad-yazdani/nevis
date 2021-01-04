import json
import logging
import os
import shutil
from io import TextIOWrapper
from subprocess import Popen, PIPE
from threading import Lock
from typing import List, Tuple, Dict

from deepsegment.deepsegment import DeepSegment

from lib.segment import Sentence
from lib.word import Word


class Decoder:
    def __init__(self, name: str, bit_rate: int, segmenter: DeepSegment, iteration: int = 1, max_active: int = 5000,
                 max_batch_size=50) -> None:
        super().__init__()
        self.name = name
        self.bit_rate = bit_rate
        self.segmenter = segmenter
        self.use_feedback = False

        self.env = os.environ.copy()
        self.env["ITERATIONS"] = str(iteration)
        self.env["MAX_ACTIVE"] = str(max_active)
        self.env["MAX_BATCH_SIZE"] = str(max_batch_size)

        self.model_dir = os.path.join(
            "/workspace/nvidia-examples/", name.lower())
        self.result_dir = os.path.join("/tmp/results/", name.lower())
        self.prep_command = "prepare_data.sh"
        self.batch_feedback_command = "run_feedback.sh"
        self.batch_command = "run_benchmark.sh"

        self.last_run = None
        # Decoding lock
        self.batch_lk = Lock()

    def initalize(self) -> None:
        prep_process = Popen(["/bin/bash", self.prep_command],
                             stdin=PIPE, stderr=PIPE, cwd=self.model_dir)
        stdout, stderr = prep_process.communicate()
        logging.debug(stdout)
        logging.debug(stderr)

    def extract_corpora(self, batch_id: int, iter_id: int = 0) -> Dict[str, object]:
        # noinspection PyBroadException
        try:
            trans_file = open(os.path.join(
                self.result_dir, str(batch_id), str(iter_id), "trans"))
            transcripts = trans_file.readlines()
            transcript_repo: Dict[str, List[str]] = {}
            for t in transcripts:
                spl = t.split(maxsplit=1)
                header = spl[0].split("_")[-1].split(".")[0]
                trans = spl[1]
                single_trans = open(os.path.join(self.result_dir, str(
                    batch_id), str(iter_id), "trans_" + header), "w")
                single_trans.write(trans)
                single_trans.close()

                archived = open(os.path.join("/root/audio/batch" +
                                             str(batch_id), "tran_" + header + ".txt"), "w")
                archived.write(trans)
                archived.close()

                transcript_repo[header] = trans.split()

            trans_int_file = open(os.path.join(self.result_dir, str(
                batch_id), str(iter_id), "trans_int_combined"))
            transcript_ints = trans_int_file.readlines()
            transcript_int_repo: Dict[str, List[int]] = {}
            for t in transcript_ints:
                spl = t.split(maxsplit=1)
                header = spl[0].split("_")[-1].split(".")[0]
                trans = spl[1]
                single_trans = open(os.path.join(self.result_dir, str(
                    batch_id), str(iter_id), "trans_int_combined_" + header), "w")
                single_trans.write(trans)
                single_trans.close()
                transcript_int_repo[header] = list(
                    map(lambda x: int(x), trans.split()))

            cmt_file = open(os.path.join(self.result_dir, str(
                batch_id), str(iter_id), "CTM.ctm"))
            convo = cmt_file.readlines()
            # noinspection PyTypeChecker
            extraction: Dict[str, TextIOWrapper] = {}
            convo_repo: Dict[str, List] = {}
            for c in convo:
                conv = c.split()[3:]
                conv = [float(conv[0]), int(conv[1])]

                meta = c.split()[0]
                header = meta.split(".", maxsplit=1)[0].split("_")[-1]
                if header in extraction:
                    extraction[header].write(str(conv[0]) + " " + str(conv[1]))
                    convo_repo[header].append(conv)
                else:
                    fd = os.path.join(self.result_dir, str(batch_id), str(iter_id), header + ".ctm")
                    # noinspection PyTypeChecker
                    extraction[header] = open(fd, "w")
                    convo_repo[header] = []
            for k in extraction.keys():
                extraction[k].close()
        except:
            print("Failed for batch ", batch_id)
            return {}

        batch_out = {}
        for key in transcript_repo.keys():
            # noinspection PyBroadException
            try:
                transcript_tokens = transcript_repo[key]
                transcript = ""
                for tt in transcript_tokens:
                    transcript += (tt + " ")
                alignment, duration = Decoder.calculate_alignment(
                    transcript_repo[key], transcript_int_repo[key], convo_repo[key])
                sentences = []
                use_lstm = True
                if use_lstm:
                    sentences = self.segmenter.segment_long(transcript)
                else:
                    # Because tensorflow is prone to breaking, I'm gonna consider every 5 words a sentence in case
                    tokens = transcript.split()
                    for index in range(len(tokens)):
                        sntsz = len(sentences)
                        if sntsz < (int(index / 5) + 1):
                            sentences.append([])
                        word = tokens[int(index)]
                        sentences[int(index / 5)].append(word)

                w_dim = 0
                aligned_sentences = list()
                for s_raw in sentences:
                    sentence = s_raw.split()
                    if use_lstm:
                        aligned_sentence = list()
                        for widx, word in enumerate(sentence):
                            w_dim += 0
                            Word(word, alignment[w_dim])
                            word_obj = Word(word, alignment[w_dim])
                            if widx == len(sentence) - 1:
                                word_obj.add_tag("is_punctuated", True)
                            aligned_sentence.append(word_obj)

                        sentence_obj = Sentence(aligned_sentence, 0)
                        aligned_sentences.append(sentence_obj)

                    for idx, _ in enumerate(aligned_sentences):
                        if idx < (len(aligned_sentences) - 1):
                            aligned_sentences[idx].length = aligned_sentences[idx +
                                                                              1].words[0].timestamp
                    aligned_sentences[(len(aligned_sentences) - 1)].length = duration
                transcript_out = {"duration": duration, "length": len(alignment), "sentences": aligned_sentences,
                                  "complete": "1"}
                out_json = open(os.path.join("/root/audio/batch" + str(batch_id), key + ".json"), "w")
                json.dump(transcript_out, out_json)
                out_json.close()
                batch_out[key] = transcript_out
            except:
                print("Failed for ", key)
        return batch_out

    def decode_batch(self, batch_id: int, iter_id: int = 0) -> Dict[str, object]:
        self.batch_lk.acquire(blocking=True)
        # set environment, start new shell
        batch_env = self.env
        batch_env["DATASET"] = os.path.join(
            "/root/audio/batch" + str(batch_id))

        if self.use_feedback:
            prep_process = Popen(["/bin/bash", self.batch_feedback_command],
                                 stdin=PIPE, stderr=PIPE, env=batch_env, cwd=self.model_dir)
            stdout, stderr = prep_process.communicate()
            logging.debug(stdout)
            logging.debug(stderr)
            num_lines = len(open(os.path.join(
                "/tmp/results", self.name, str(batch_id), "0", "trans")).readlines())
            if num_lines < 2:
                self.use_feedback = False
                shutil.rmtree(os.path.join(
                    "/tmp/results", self.name, str(batch_id)))
                prep_process = Popen(["/bin/bash", self.batch_command],
                                     stdin=PIPE, stderr=PIPE, env=batch_env, cwd=self.model_dir)
                stdout, stderr = prep_process.communicate()
                logging.debug(stdout)
                logging.debug(stderr)
        else:
            prep_process = Popen(["/bin/bash", self.batch_command],
                                 stdin=PIPE, stderr=PIPE, env=batch_env, cwd=self.model_dir)
            stdout, stderr = prep_process.communicate()
            logging.debug(stdout)
            logging.debug(stderr)

        # batch_env = self.env
        prep_process = Popen(["/usr/bin/gzip", "-d", os.path.join(
            self.result_dir, str(batch_id), str(iter_id), "lat_aligned.gz")], stdin=PIPE)
        stdout, stderr = prep_process.communicate()
        logging.debug(stdout)
        logging.debug(stderr)

        ctm_file = os.path.join(self.result_dir, str(
            batch_id), str(iter_id), "CTM.ctm")

        lattice_align_command: str = ""
        lattice_align_command += "/opt/kaldi/src/latbin/lattice-align-words-lexicon --partial-word-label=4324 " \
                                 "/workspace/models/aspire/data/lang_chain/phones/align_lexicon.int " \
                                 "/workspace/models/aspire/final.mdl"
        lattice_align_command += (" ark:" + os.path.join(self.result_dir,
                                                         str(batch_id), str(iter_id), "lat_aligned"))
        lattice_align_command += " ark:- | /opt/kaldi/src/latbin/lattice-1best ark:- ark:- | " \
                                 "/opt/kaldi/src/latbin/nbest-to-ctm ark:- "
        lattice_align_command += ctm_file
        prep_process = Popen(lattice_align_command, stdin=PIPE, shell=True)
        stdout, stderr = prep_process.communicate()
        logging.debug(stdout)
        logging.debug(stderr)

        corpora = self.extract_corpora(batch_id)

        if self.last_run is not None:
            self.last_run += 1
        else:
            self.last_run = 0

        self.batch_lk.release()
        return corpora

    def clear_results(self) -> None:
        if os.path.exists(self.result_dir):
            os.rmdir(self.result_dir)

    @staticmethod
    def calculate_alignment(words: List[str], idx: List[int], lats: List[List]) -> Tuple[List, float]:
        word_table: Dict[int, str] = dict()
        alignment = []

        len_words = len(words)
        len_idx = len(idx)
        len_lats = len(lats)
        assert len_words == len_idx
        if len_idx > len_lats:
            lats.insert(0, [0.0, idx[0]])
            if lats[0][0] == lats[1][0]:
                lats[1][0] = (lats[2][0] / 2)

        for i in range(len_idx):
            wt_idx = idx[i]
            word_table[wt_idx] = words[i]
        offset = 0.0
        for i in range(len_lats):
            olat = lats[i][0]
            if olat == 0.0:
                # noinspection PyBroadException
                try:
                    next_lat = lats[i + 1][0]
                    olat = next_lat / 2
                except:
                    olat = 0.05
            offset += olat
            lat_i = int(lats[i][1])
            w = word_table[lat_i]
            align = offset - lats[i][0]
            alignment.append([w, align])
        return alignment, offset

    @staticmethod
    def fetch_transcript(batch_id: int, corpus_id: str) -> object:
        out_json = open(os.path.join("/root/audio/batch" + str(batch_id), corpus_id + ".json"), "r")
        out_json = json.load(out_json)
        return out_json
