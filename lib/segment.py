PARAMS_PATH = "/mnt/libspeech/model/deep_punct/deeppunct_params_en"
CHECKPOINT_PATH = "/mnt/libspeech/model/deep_punct/deeppunct_checkpoint_wikipedia"


class Sentence(dict):

    def __init__(self, words, length):
        super().__init__(words=words, length=length)
        self.words = words
        self.length = length


class Segmenter:

    def __init__(self, segmenter) -> None:
        super().__init__()
        self.segmenter = segmenter

    @staticmethod
    def _extract_words(segment, punctuated):
        raw_words = str(segment).split()
        punctuated_words = punctuated.split()

        # TODO : Dummy punctuation
        first_word = punctuated_words[0]
        first_char = (first_word[0]).upper()
        rest_word = first_word[1:]
        punctuated_words[0] = first_char + rest_word
        punctuated_words[-1] += "."

        if len(raw_words) != len(punctuated_words):
            # TODO : This should be an error but for now we hack around
            # raise Exception("Extra words added by punct :/")
            first = punctuated_words[0]
            punctuated_words = raw_words
            punctuated_words[0] = first
            punctuated_words[-1] = punctuated_words[-1] + "."

        punctuated_indexes = list()
        for idx in range(len(raw_words)):
            if raw_words[idx] != punctuated_words[idx] and len(raw_words[idx]) != len(punctuated_words[idx]):
                punctuated_indexes.append(idx)
            else:
                punctuated_indexes.append(None)

        return punctuated_words, punctuated_indexes

    def segment(self, transcript):
        # The default language is 'en'
        segments = self.segmenter.segment_long(transcript)
        punctuated_sequences = segments
        sentences = list()
        # Parallel
        for idx in range(len(segments)):
            seq = punctuated_sequences[idx]
            seg = segments[idx]
            words = Segmenter._extract_words(seg, seq)
            sentences.append(words)

        return sentences
