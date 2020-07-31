#!/usr/bin/python3

import wave
import sys

# from lib.audio import stereo_to_mono, wav_from_mp4
from tools.perf import Perf


def compare_frames(wav1, wav2):
    perf = Perf(take_intervals=True)

    w_one = wave.open(wav1, "r")
    w_two = wave.open(wav2, "r")

    nframes_one = w_one.getnframes()
    nframes_two = w_two.getnframes()

    frames_one = w_one.readframes(nframes_one)
    frames_two = w_two.readframes(nframes_two)

    if frames_one == frames_two:
        print('exactly the same')
    else:
        print('not a match')

    print(perf.elapsed())

