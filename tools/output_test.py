#!/usr/bin/python3

import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--dump", required=True)
parser.add_argument("--human", action="store_true")
args = parser.parse_args()
JSON_DUMP = open(args.dump, "r")
VIEW = args.human


def read_dump(json_dump):
    in_transcript = json.load(json_dump)
    sent_align = read_sent_alignment(in_transcript["sentences"])
    return sent_align


def read_sent_alignment(in_sentences):
    alignment = list()
    for s in in_sentences:
        align = s["words"][0]["timestamp"]
        sentence = ""
        for w_idx in range(len(s["words"]) - 1):
            sentence += s["words"][w_idx]["value"]
            sentence += " "
        sentence += s["words"][-1]["value"]
        alignment.append([align, sentence])
    return alignment


transcript = read_dump(JSON_DUMP)
for t in transcript:
    stamp = float(t[0])
    minutes = int(stamp / 60)
    seconds = stamp - (minutes * 60)
    sent = t[1]
    if VIEW:
        print(str(minutes) + ":" + str(format(seconds, '.2f')) + " | " + sent)
    else:
        print(str(stamp) + " | " + str(sent))
