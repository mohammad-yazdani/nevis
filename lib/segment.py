# from deepcorrect import DeepCorrect

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
        puncted_words = punctuated.split()
        
        # TODO : Dummy punctuation
        first_word = puncted_words[0]
        first_char = (first_word[0]).upper()
        rest_word = first_word[1:]
        puncted_words[0] = first_char + rest_word
        puncted_words[-1] += "."

        if len(raw_words) != len(puncted_words):
            # TODO : This should be an error but for now we hack around
            # raise Exception("Extra words added by punct :/")
            first = puncted_words[0]
            puncted_words = raw_words
            puncted_words[0] = first
            puncted_words[-1] = puncted_words[-1] + "."

        puncted_indexes = list()
        for idx in range(len(raw_words)):
            if raw_words[idx] != puncted_words[idx] and len(raw_words[idx]) != len(puncted_words[idx]):
                puncted_indexes.append(idx)
            else:
                puncted_indexes.append(None)

        return puncted_words, puncted_indexes

    # TODO : Use later
    # @staticmethod
    # def _punctuate(sentences):
    #     corrector = DeepCorrect(params_path=PARAMS_PATH, checkpoint_path=CHECKPOINT_PATH)
    #     corrections = list()
    #     for s in sentences:
    #        correction = corrector.correct(s)[0]["sequence"]
    #        corrections.append(correction)
    #    return corrections

    def segment(self, transcript):
        # The default language is 'en'
        segments = self.segmenter.segment_long(transcript)
        # puncted_sequences = Sentence._punctuate(segments)
        # TODO : Quick fix hack
        puncted_sequences = segments 
        sentences = list()
        # Parallel
        for idx in range(len(segments)):
            seq = puncted_sequences[idx]
            seg = segments[idx]
            words = Sentence._extract_words(seg, seq)
            sentences.append(words)

        return sentences
