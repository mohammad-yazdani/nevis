#!/usr/bin/python3
import sys
import os
import shutil


corps_dir = "common_words"


def extract_corp(glob_obj, corp):
    prefix = corps_dir + "/" + corp + "/"
    if os.path.exists(prefix):
        shutil.rmtree(prefix)
    os.mkdir(prefix)

    for key, val in glob_obj[corp].items():
        # print(key)
        for idx, v in enumerate(val):
            output = key + "_" + str(idx) + ".wav"
            inp = v[0]
            start = v[1]
            dur = v[2]
            # print(inp, start, dur, output)
            
            try:
                os.system("ffmpeg -loglevel quiet -i " + inp + " -ss 0" + start + " -t 0" + dur + " -c copy " + prefix + output)
                crum = corp + " > " + key
                sys.stdout.write(crum + " : %d   \r" % (idx) )
                sys.stdout.flush()
            except:
                print(prefix, output, " failed!")
    sys.stdout.flush()
    print("[" + corp + " done.]")


if os.path.exists(corps_dir):
    shutil.rmtree(corps_dir)
os.mkdir(corps_dir)

in_data = sys.stdin.read().splitlines()
in_data = list(map(lambda x: x.split(), in_data))

corps = set(map(lambda x: x[0], in_data))
glob = dict()
for d in in_data:
    glob[d[0]] = dict()

for d in in_data:
    glob[d[0]][d[1]] = []

for d in in_data:
    glob[d[0]][d[1]].append([d[2], d[3], d[4]])

for c in corps:
    extract_corp(glob, c)
# print(glob)

