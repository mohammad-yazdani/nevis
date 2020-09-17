from kaldiasr.nnet3 import KaldiNNet3OnlineModel, KaldiNNet3OnlineDecoder
import os

from tools.file_io import delete_if_exists


class Decoder:
    MODELDIR = '/mnt/libspeech/model/kaldi-generic-en-tdnn_fl-r20190609'

    def __init__(self, model=None):
        if model is None:
            model = Decoder.MODELDIR
        self.model = model
        self.kaldi_model = KaldiNNet3OnlineModel(self.model)
        self.decoder = KaldiNNet3OnlineDecoder(self.kaldi_model)

    def decode(self, WAVFILE):
        # try:
        if self.decoder.decode_wav_file(WAVFILE):

            s, lk = self.decoder.get_decoded_string()
            align = self.decoder.get_word_alignment()

            os.remove(WAVFILE)

            for word_idx in range(len(align[0])):
                str_word = align[0][word_idx].decode("utf-8")
                align[0][word_idx] = str_word

            out_dict = dict()
            out_dict["transcript"] = s
            out_dict["likelihood"] = lk
            out_dict["model"] = os.path.basename(Decoder.MODELDIR)
            out_dict["alignment"] = align
            return out_dict

        else:
            print("***ERROR: decoding of %s failed." % WAVFILE)
            return "error"

        # except Exception as error:
        #     delete_if_exists("/tmp/transcribe.mp4")
        #     print("ERROR: " + str(error))
