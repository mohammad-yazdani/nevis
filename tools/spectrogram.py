#!/usr/bin/python3

import sys
import matplotlib.pyplot as plt
from scipy import signal
from scipy.io import wavfile


def spec(wav_file):
    sample_rate, samples = wavfile.read(wav_file)
    frequencies, times, spectrogram = signal.spectrogram(samples, sample_rate)
    
    try:
        plt.pcolormesh(times, frequencies, spectrogram)
        plt.imshow(spectrogram)
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time [sec]')
        # plt.show()
        plt.savefig(wav_file + ".png", format="png") # TODO : Can change to svg
    except:
        print(wav_file, " failed")
        return 0, 0, 0
    return len(times), len(frequencies), len(spectrogram)


failed = 0
for idx, arg in enumerate(sys.argv[1:]):
    t, f, s = spec(arg)
    if (t + f + s) == 0:
        failed += 1
        continue
    msg = "times: " + str(t) + " freq: " + str(t) + " spec: " + str(s)
    sys.stdout.write("Graphed : %d | Failed: %d  \r" % (idx, failed) )
    # sys.stdout.write(msg + " \r") ## TODO : CAN use for debugging
    sys.stdout.flush()

print("Graphed : " + str(idx) + " | Failed: " + str(failed))

