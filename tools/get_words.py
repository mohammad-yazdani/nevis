#!/usr/bin/python3
import sys
import json


def main(args):
    output = []
    for arg in args:
        dump = open(arg, "r")
        obj = json.load(dump)
        local_out = []
        for sen in obj["sentences"]:
            for word in sen["words"]:
                if word["tags"]["is_punctuated"]:
                    value = word["value"][:-1]
                else:
                    value = word["value"]
                local_out.append([value, word["timestamp"]])
        output.append(local_out)
    return output


if __name__ == "__main__":
    hi_out = main(sys.argv[1:])
    for out in hi_out:
        for o in out:
            line = o[0]
            for s in o[1:]:
                line += " "
                line += str(s)
            print(line)
        print("")

