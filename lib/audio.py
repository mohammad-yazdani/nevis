from lib.batch import ToDecode
import os
import time
import subprocess
from pydub import AudioSegment
from tools.file_io  import delete_if_exists

class Audio:
    epoch: int = 0

    @staticmethod
    def prepare(self, mp4_file) -> ToDecode:
        wav_out = os.path.join(self.prefix, "audio" + str(self.epoch) + ".wav")
        delete_if_exists(wav_out)
        self.epoch += 1
        ffmpeg_command = "ffmpeg -i " + mp4_file + " -vn -acodec pcm_s16le -ar 16000 -ac 2 " + wav_out
        currtime = str(int(time.time()))
        with open('/tmp/ffmpeg' + currtime + '.log', "w") as outfile:
            subprocess.run(ffmpeg_command, shell=True, stderr=outfile)
        sound = AudioSegment.from_wav(wav_out)
        sound = sound.set_channels(1)
        sound.export(wav_out, format="wav")
        return ToDecode(wav_out, Audio._media_duration(wav_out))

    @staticmethod
    def get_prefix() -> str:
        return "/root/audio"

    # Code straight from https://stackoverflow.com/a/3844467
    @staticmethod
    def _media_duration(filename):
        result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of",
            "default=noprint_wrappers=1:nokey=1", filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        return float(result.stdout)
