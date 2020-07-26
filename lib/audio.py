import os
import time
import subprocess
from pydub import AudioSegment

from tools.file_io import delete_if_exists


def wav_from_mp4(mp4_file):
    wav_out = mp4_file + ".wav"
    delete_if_exists(wav_out)

    ffmpeg_command = "ffmpeg -i " + mp4_file + " -vn -acodec pcm_s16le -ar 16000 -ac 2 " + wav_out
    currtime = str(int(time.time()))
    with open('/tmp/ffmpeg' + currtime + '.log', "w") as outfile:
        subprocess.run(ffmpeg_command, shell=True, stderr=outfile)
    
    return wav_out


def stereo_to_mono(stereo_file):
    mono_out = stereo_file + ".mono"
    delete_if_exists(mono_out)
    
    sound = AudioSegment.from_wav(stereo_file)
    sound = sound.set_channels(1)
    sound.export(mono_out, format="wav")

    delete_if_exists(stereo_file)

    return os.path.abspath(mono_out)


# Code straight from https://stackoverflow.com/a/3844467
def media_duration(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    return float(result.stdout)


def prepare_input(mp4_file):
    stereo_wav = wav_from_mp4(mp4_file)
    return stereo_to_mono(stereo_wav), media_duration(mp4_file)
