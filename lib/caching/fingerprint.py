import textdistance
import sys
from typing import Tuple

BLOCK_SZ = 256

SIM_THRESHOLD = 0.9
HARD_MIN = 0.9


def compare_fp(fp0: str, fp1: str) -> Tuple[float, float]:
    offset = 0

    simis = []
    while offset < min(len(fp0), len(fp1)):
        op0 = fp0[offset:(offset + BLOCK_SZ)]
        op1 = fp1[offset:(offset + BLOCK_SZ)]
        offset += BLOCK_SZ
        simi = textdistance.ratcliff_obershelp.similarity(op0, op1)
        simis.append(simi)

    min_simi = min(simis)
    avg = 0
    for s in simis:
        avg += s
    avg = avg / len(simis)

    return min_simi, avg


def is_similar(fp0, fp1) -> bool:
    minn, avg = compare_fp(fp0, fp1)
    return minn >= HARD_MIN and avg >= SIM_THRESHOLD


if __name__ == "__main__":
    filep0 = open(sys.argv[1]).read()
    filep1 = open(sys.argv[2]).read()
    print(is_similar(filep0, filep1))
