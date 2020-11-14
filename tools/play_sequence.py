#!/usr/local/bin/python3
import subprocess
import os
import sys


def play_seq(seq_dir):
    files = os.listdir(seq_dir)
    files = sorted(files)

    for f in files:
        print("afplay " + str(os.path.join(seq_dir, f)))
        subprocess.run("afplay " + str(os.path.join(seq_dir, f)), stdout=subprocess.PIPE,stdin=subprocess.PIPE, shell=True)


# play_seq(sys.argv[1])
