import codecs
import logging
import os
from os import mkdir
from os.path import exists
import subprocess
from typing import Optional

from pydub.audio_segment import AudioSegment

from lib.batch import ToDecode

CORPUS_HASH_LEN = 16


class Audio:
    epoch: int = 0

    @staticmethod
    def prepare(media: bytes, bit_rate: int) -> Optional[ToDecode]:
        corpus_id = codecs.encode(os.urandom(CORPUS_HASH_LEN), 'hex').decode()
        wav_in = os.path.join(Audio.get_prefix(), corpus_id + ".pre.wav")
        wav_out = os.path.join(Audio.get_prefix(), corpus_id + ".wav")
        # while os.path.exists(wav_out) or os.path.exists(wav_in):
        #     corpus_id = codecs.encode(os.urandom(CORPUS_HASH_LEN), 'hex').decode()
        #     wav_in = os.path.join(Audio.get_prefix(), corpus_id + ".pre.wav")
        #     wav_out = os.path.join(Audio.get_prefix(), corpus_id + ".wav")

        if not exists(Audio.get_prefix()):
            mkdir(Audio.get_prefix())

        in_wav = open(wav_in, "wb")
        in_wav.write(media)
        in_wav.close()

        Audio.epoch += 1
        ffmpeg_command = "ffmpeg -i " + wav_in + " -vn -acodec pcm_s16le -ar " + str(bit_rate) + " -ac 2 " + wav_out
        p = subprocess.Popen(ffmpeg_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = p.communicate()
        if p.returncode != 0:
            logging.debug(output.decode("utf-8"))
            logging.error(err.decode("utf-8"))
            return None

        sound = AudioSegment.from_wav(wav_out)
        sound = sound.set_channels(1)
        sound.export(wav_out, format="wav")
        return ToDecode(wav_out, Audio._media_duration(wav_out), corpus_id)

    @staticmethod
    def get_prefix() -> str:
        return "/root/audio"

    # Code straight from https://stackoverflow.com/a/3844467
    @staticmethod
    def _media_duration(filename) -> float:
        result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                 "format=duration", "-of",
                                 "default=noprint_wrappers=1:nokey=1", filename],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        return float(result.stdout)
