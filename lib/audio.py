from lib.batch import ToDecode
import os
import subprocess
from tools.file_io  import delete_if_exists
from pydub.audio_segment import AudioSegment

class Audio:
    epoch: int = 0

    @staticmethod
    def prepare(mp4_file: str, bit_rate: int) -> ToDecode:
        wav_out = os.path.join(Audio.get_prefix(), "audio" + str(Audio.epoch) + ".wav")
        delete_if_exists(wav_out)
        Audio.epoch += 1
        ffmpeg_command = "ffmpeg -i " + mp4_file + " -vn -acodec pcm_s16le -ar " + str(bit_rate) + " -ac 2 " + wav_out        
        with open('/dev/null', "w") as outfile:
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
    def _media_duration(filename) -> float:
        result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of",
            "default=noprint_wrappers=1:nokey=1", filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        return float(result.stdout)
