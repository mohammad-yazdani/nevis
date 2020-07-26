from deepsegment import DeepSegment
from deepcorrect import DeepCorrect

PARAMS_PATH = "/mnt/libspeech/model/deep_punct/deeppunct_params_en"
CHECKPOINT_PATH = "/mnt/libspeech/model/deep_punct/deeppunct_checkpoint_wikipedia"


class Sentence:

    def __init__(self, words, length):
        self.words = words
        self.length = length

    @staticmethod
    def _extract_words(segment, punctuated):
        raw_words = str(segment).split()
        puncted_words = punctuated.split()
        if len(raw_words) != len(puncted_words):
            raise Exception("Extra words added by punct :/")
        puncted_indexes = list()
        for idx in range(len(raw_words)):
            if raw_words[idx] != puncted_words[idx] and len(raw_words[idx]) != len(puncted_words[idx]):
                puncted_indexes.append(idx)
            else:
                puncted_indexes.append(None)

        return puncted_words, puncted_indexes

    @staticmethod
    def _punctuate(sentences):
        corrector = DeepCorrect(params_path=PARAMS_PATH, checkpoint_path=CHECKPOINT_PATH)
        corrections = list()
        for s in sentences:
            correction = corrector.correct(s)[0]["sequence"]
            corrections.append(correction)
        return corrections

    @staticmethod
    def segment(transcript):
        # The default language is 'en'
        segmenter = DeepSegment("en")
        segments = segmenter.segment_long(transcript)
        puncted_sequences = Sentence._punctuate(segments)

        sentences = list()
        # Parallel
        for idx in range(len(segments)):
            seq = puncted_sequences[idx]
            seg = segments[idx]
            words = Sentence._extract_words(seg, seq)
            sentences.append(words)

        return sentences
