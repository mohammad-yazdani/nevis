#!/usr/bin/python3

import wave
import sys
from tools.perf import Perf

perf = Perf(take_intervals=True)

w_one = wave.open(sys.argv[1], "r")
w_two = wave.open(sys.argv[2], "r")

if w_one.readframes() == w_two.readframes():
    print('exactly the same')
else:
    print('not a match')

print(perf.elapsed())
