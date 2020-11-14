#!/usr/local/bin/python3
import sys
import subprocess
import os

input_fname = sys.argv[1]
output_fname = input_fname.split(".")[0] + ".wav"

command = ['ffmpeg', '-nostats', '-loglevel', '0', '-i', input_fname, '-ac', '1', '-f', 'wav', output_fname]
subprocess.run(command,stdout=subprocess.PIPE,stdin=subprocess.PIPE)
print(os.path.abspath(output_fname))
