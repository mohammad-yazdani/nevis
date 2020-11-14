#!/usr/bin/python3
import json
import sys
import os
import math
import datetime

from get_words import main as words


def fl_sec_to_hhmmssxxx(s):
    sec = math.floor(s)
    return str(datetime.timedelta(seconds=s))

def main(args):
    video_src = []
    video_name = []
    for arg in args:
        video = os.path.basename(arg).split('.')[0].replace("_transcript_dump", "")
        video_path = "../misc/ready/audio/" + video + ".wav"
        assert os.path.exists(video_path)
        video_src.append(video_path)
        video_name.append(video)

    filts = []
    for l in sys.stdin.read().splitlines():
        filts.append(l)
    ws = words(args)
    
    for arg_idx, wset in enumerate(ws):
        # print(wset[0][1], file=sys.stderr)  TODO : Trash
        limiter = 0
        for idx, w in enumerate(wset[:-1]):
            # if limiter > 200:
            #    break;
            if w[0] in filts: 
                # TODO : FFmpeg editing
                start_fl = float(w[1])
                end_fl = float(wset[idx + 1][1])
                start = fl_sec_to_hhmmssxxx(start_fl)[:-3]
                dur = fl_sec_to_hhmmssxxx(end_fl - start_fl)[:-3]
                print(w[0], "\t", video_name[arg_idx], video_src[arg_idx], "\t", start, dur)
                limiter += 1


if __name__ == "__main__":
    main(sys.argv[1:])

