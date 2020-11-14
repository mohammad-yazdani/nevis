#!/bin/bash

cd tools
./get_words.py ../transcripts/ahoo_lectures_oct15_* | ./top_words.py | ./get_timestamps.py ../transcripts/ahoo_lectures_oct15_* | ./union_tree.py
./spectrogram.py the/*
cd ..

