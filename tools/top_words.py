#!/usr/bin/python3
import sys
from collections import Counter


n = 20
if len(sys.argv) > 1:
    n = int(sys.argv[1])

words = [[]]
idx = 0
for line in sys.stdin.readlines():
    if line.strip() == '':
        idx += 1
        words.append([])
    else:
        words[idx].append(line.split()[0])

words = list(filter(lambda x: len(x) > 0, words))
top_ns = []
for wset in words:
    top_ns.append([])
    top_words = Counter(wset)
    count = 0
    top_words = sorted(top_words.items(), key=lambda item: item[1])
    top_words.reverse()
    
    for key, value in top_words:
        if int(value) > 1 and count < n:
            top_ns[-1].append(key)
            count += 1
 
tops = set(top_ns[0])
for ws in top_ns[1:]:
    for w in ws:
        tops.intersection(w)

for w in tops:
    print(w)

