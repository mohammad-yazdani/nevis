#!/usr/bin/python3

import wave
import sys

# from lib.audio import stereo_to_mono, wav_from_mp4
from tools.perf import Perf


def get_frames(wav_file):
    w = wave.open(wav_file, "r")

    nframes = w.getnframes()

    frames = w.readframes(nframes)
    return frames


def compare_frames(wav1, wav2):
    perf = Perf(take_intervals=True)

    frames_one = get_frames(wav1)
    frames_two = get_frames(wav2)

    if frames_one == frames_two:
        print('exactly the same')
    else:
        print('not a match')

    print(perf.elapsed())


compare_frames(sys.argv[1], sys.argv[2])

